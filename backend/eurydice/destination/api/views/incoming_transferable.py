import base64
from typing import cast

from django import http
from django.contrib.auth.models import AnonymousUser
from django.db.models.query import QuerySet
from django_filters import rest_framework as filters
from rest_framework import decorators, mixins, renderers, status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from eurydice.common.api import pagination, permissions
from eurydice.common.logging.logger import LOG_KEY, logger
from eurydice.destination.api import exceptions as api_exceptions
from eurydice.destination.api import filters as destination_filters
from eurydice.destination.api import negotiation, serializers
from eurydice.destination.api import permissions as destination_permissions
from eurydice.destination.api.docs import decorators as documentation
from eurydice.destination.core import models
from eurydice.destination.storage import fs

_TRANSFERABLE_STATE_TO_ERROR = {
    models.IncomingTransferableState.ONGOING: api_exceptions.TransferableOngoingError,
    models.IncomingTransferableState.EXPIRED: api_exceptions.TransferableExpiredError,
    models.IncomingTransferableState.REVOKED: api_exceptions.TransferableRevokedError,
    models.IncomingTransferableState.ERROR: api_exceptions.TransferableErroredError,
    models.IncomingTransferableState.REMOVED: api_exceptions.TransferableRemovedError,
}


def _fs_response(
    instance: models.IncomingTransferable, filename: str, headers: dict[str, str]
) -> http.FileResponse | Response:
    try:
        data = open(fs.file_path(instance), "rb")  # noqa: SIM115
        resp = http.FileResponse(
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
        user_id = cast(AnonymousUser, self.request.user).id
        logger.info({LOG_KEY: "incoming_transferable_get_queryset", "username": self.request.user.username})
        return queryset.filter(user_profile__user__id=user_id).order_by("-created_at")

    def perform_destroy(self, instance: models.IncomingTransferable) -> None:
        """Remove the IncomingTransferable from the storage and from the database."""
        if instance.state != models.IncomingTransferableState.SUCCESS:
            raise api_exceptions.UnsuccessfulTransferableError

        fs.delete(instance)
        instance.mark_as_removed()

    @decorators.action(
        detail=True,
        url_path="download",
        url_name="download",
        renderer_classes=[
            renderers.JSONRenderer,
        ],
        content_negotiation_class=negotiation.IgnoreClientContentNegotiation,
    )
    def download(
        self,
        request: Request,
        *args,
        **kwargs,
    ) -> http.FileResponse | Response:
        """Download the file corresponding to an IncomingTransferable."""
        instance = self.get_object()

        if instance.state != models.IncomingTransferableState.SUCCESS:
            raise _TRANSFERABLE_STATE_TO_ERROR[instance.state]

        filename = instance.name or str(instance.id)
        headers = {
            **instance.user_provided_meta,
            "Digest": "SHA=" + base64.b64encode(instance.sha1).decode("utf-8"),
        }

        return _fs_response(instance, filename, headers)

    @decorators.action(
        methods=["DELETE"],
        detail=False,
        url_path="",
        url_name="destroy-all",
        renderer_classes=[
            renderers.JSONRenderer,
        ],
        content_negotiation_class=negotiation.IgnoreClientContentNegotiation,
    )
    def delete(self, request: Request) -> Response:
        """Delete all successful IncomingTransferable to free the space"""
        logger.info({LOG_KEY: "incoming_transferable_delete", "username": str(request.user.username)})

        successful_transferables = self.get_queryset().filter(state=models.IncomingTransferableState.SUCCESS)
        if len(successful_transferables) == 0:
            return Response("Aucun fichier à supprimer", 200)
        for instance in successful_transferables:
            self.perform_destroy(instance)

        logger.info(
            {
                LOG_KEY: "incoming_transferable_delete",
                "username": str(request.user.username),
                "status": "success",
                "successful_transferables": len(successful_transferables),
            }
        )

        if len(successful_transferables) == 1:
            return Response("1 fichier a été supprimé", 200)
        return Response(f"{len(successful_transferables)} fichiers ont été supprimés", 200)


__all__ = ("IncomingTransferableViewSet",)
