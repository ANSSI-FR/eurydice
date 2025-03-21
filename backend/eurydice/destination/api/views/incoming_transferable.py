import base64
import logging
from typing import Union

from django.conf import settings
from django.db.models.query import QuerySet
from django_filters import rest_framework as filters
from rest_framework import decorators
from rest_framework import mixins
from rest_framework import renderers
from rest_framework import status
from rest_framework import viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from eurydice.common import exceptions
from eurydice.common import minio
from eurydice.common.api import pagination
from eurydice.common.api import permissions
from eurydice.destination.api import exceptions as api_exceptions
from eurydice.destination.api import filters as destination_filters
from eurydice.destination.api import negotiation
from eurydice.destination.api import permissions as destination_permissions
from eurydice.destination.api import responses
from eurydice.destination.api import serializers
from eurydice.destination.api.docs import decorators as documentation
from eurydice.destination.core import models
from eurydice.destination.storage import fs

logger = logging.getLogger(__name__)

_TRANSFERABLE_STATE_TO_ERROR = {
    models.IncomingTransferableState.ONGOING: api_exceptions.TransferableOngoingError,
    models.IncomingTransferableState.EXPIRED: api_exceptions.TransferableExpiredError,
    models.IncomingTransferableState.REVOKED: api_exceptions.TransferableRevokedError,
    models.IncomingTransferableState.ERROR: api_exceptions.TransferableErroredError,
    models.IncomingTransferableState.REMOVED: api_exceptions.TransferableRemovedError,
}


def _minio_response(
    instance: models.IncomingTransferable, filename: str, headers: dict[str, str]
) -> Union[responses.ForwardedS3FileResponse, Response]:
    try:
        return responses.ForwardedS3FileResponse(
            bucket_name=instance.s3_bucket_name,
            object_name=instance.s3_object_name,
            filename=filename,
            extra_headers=headers,
        )
    except exceptions.S3ObjectNotFoundError:
        instance.mark_as_error()
        # Manually return a 500 response instead of raising an error
        # so that the DB transaction is committed.
        return Response(
            data="Couldn't retrieve transferable",
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def _fs_response(
    instance: models.IncomingTransferable, filename: str, headers: dict[str, str]
) -> Union[responses.http.FileResponse, Response]:  # type: ignore
    try:
        data = open(fs.file_path(instance), "rb")  # noqa: SIM115
        resp = responses.http.FileResponse(  # type: ignore
            data,
            filename=filename,
            headers={
                "Content-Length": instance.size,
                **headers,
            },
            as_attachment=True,
            # manually override Content-Type to prevent mime sniffing
            content_type="application/octet-stream",
        )
        return resp
    except OSError:
        instance.mark_as_error()
        # Manually return a 500 response instead of raising an error
        # so that the DB transaction is committed.
        return Response(
            data="Couldn't retrieve transferable",
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@documentation.incoming_transferable
class IncomingTransferableViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Retrieve, list and delete IncomingTransferables."""

    serializer_class = serializers.IncomingTransferableSerializer
    queryset = models.IncomingTransferable.objects.all()
    pagination_class = pagination.EurydiceSessionPagination
    permission_classes = [
        permissions.IsTransferableOwner,
        destination_permissions.IsAssociatedUser,
    ]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = destination_filters.IncomingTransferableFilter

    def get_queryset(self) -> QuerySet[models.IncomingTransferable]:
        """Filter queryset to only retrieve IncomingTransferables for the current
        user.
        """
        queryset = super().get_queryset()
        return queryset.filter(user_profile__user__id=self.request.user.id).order_by(
            "-created_at"
        )

    def perform_destroy(self, instance: models.IncomingTransferable) -> None:
        """Remove the IncomingTransferable from the storage and from the database."""
        if instance.state != models.IncomingTransferableState.SUCCESS:
            raise api_exceptions.UnsuccessfulTransferableError

        if settings.MINIO_ENABLED:
            logger.debug("Remove file from MinIO.")
            minio.client.remove_object(
                bucket_name=instance.s3_bucket_name, object_name=instance.s3_object_name
            )
            logger.debug("File successfully removed from MinIO.")
        else:
            logger.debug("Remove file from filesystem.")
            fs.delete(instance)
            logger.debug("File successfully removed from filesystem.")

        instance.mark_as_removed()
        logger.debug("IncomingTransferable marked as removed in database.")

    @decorators.action(
        detail=True,
        url_path="download",
        url_name="download",
        renderer_classes=[
            # JSONRenderer is only used for error responses and not for successful ones
            # since successful requests use the ForwardedS3FileResponse
            renderers.JSONRenderer,
        ],
        content_negotiation_class=negotiation.IgnoreClientContentNegotiation,
    )
    def download(
        self,
        request: Request,
        *args,
        **kwargs,
    ) -> Union[  # type: ignore
        responses.ForwardedS3FileResponse, responses.http.FileResponse, Response
    ]:
        """Download the file corresponding to an IncomingTransferable."""
        logger.debug("Request IncomingTransferableState from database.")
        instance = self.get_object()

        if instance.state != models.IncomingTransferableState.SUCCESS:
            raise _TRANSFERABLE_STATE_TO_ERROR[instance.state]

        filename = instance.name or str(instance.id)
        headers = {
            **instance.user_provided_meta,
            "Digest": "SHA=" + base64.b64encode(instance.sha1).decode("utf-8"),
        }

        if settings.MINIO_ENABLED:
            return _minio_response(instance, filename, headers)
        else:
            return _fs_response(instance, filename, headers)

    @decorators.action(
        methods=["DELETE"],
        detail=False,
        url_path="",
        url_name="destroy-all",
        renderer_classes=[
            # JSONRenderer is only used for error responses and not for successful ones
            # since successful requests use the ForwardedS3FileResponse
            renderers.JSONRenderer,
        ],
        content_negotiation_class=negotiation.IgnoreClientContentNegotiation,
    )
    def delete(self, request: Request) -> Response:
        """Delete all successful IncomingTransferable to free the space"""
        logger.debug("Removing all files.")
        successful_transferables = self.get_queryset().filter(
            state=models.IncomingTransferableState.SUCCESS
        )
        if len(successful_transferables) == 0:
            return Response("Aucun fichier à supprimer", 200)
        for instance in successful_transferables:
            self.perform_destroy(instance)
        logger.debug("Files successfully removed.")
        if len(successful_transferables) == 1:
            return Response("1 fichier a été supprimé", 200)
        return Response(
            f"{len(successful_transferables)} fichiers ont été supprimés", 200
        )


__all__ = ("IncomingTransferableViewSet",)
