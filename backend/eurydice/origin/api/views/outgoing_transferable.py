import hashlib
import io
import logging
import uuid
from typing import BinaryIO
from typing import List
from typing import Optional
from typing import cast

from django.conf import settings
from django.db import transaction
from django.db.models import query
from django.utils import decorators
from django.utils import timezone
from django_filters import rest_framework as filters
from rest_framework import exceptions as drf_exceptions
from rest_framework import mixins
from rest_framework import request as drf_request
from rest_framework import response as drf_response
from rest_framework import status
from rest_framework import throttling
from rest_framework import viewsets

from eurydice.common import enums
from eurydice.common.api import pagination
from eurydice.common.api import permissions
from eurydice.origin.api import exceptions
from eurydice.origin.api import filters as origin_filters
from eurydice.origin.api import parsers
from eurydice.origin.api import serializers
from eurydice.origin.api import utils
from eurydice.origin.api.docs import decorators as documentation
from eurydice.origin.core import models
from eurydice.origin.storage import fs

logger = logging.getLogger(__name__)

_UPLOAD_FILEOBJ_MAX_CONCURRENCY = 1
_UNKNOWN_FILEOBJ_LENGTH = -1

_hash_func = hashlib.sha1


def _storage_exists(transferable_range: models.TransferableRange) -> bool:
    return fs.file_path(transferable_range).parent.is_dir()


def __create_storage_folder(transferable_range: models.TransferableRange) -> None:
    """
    Create the OutgoingTransferable folder to store data.
    """
    file_path = fs.file_path(transferable_range)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    logger.debug("Folder for OutgoingTransferables created.")


def _store_transferable_range(
    stream_partition: utils.StreamPartition,
    transferable: models.OutgoingTransferable,
) -> None:
    """Upload TransferableRange's data to fs and update the transferable's size.

    Args:
        stream_partition: StreamPartition to read the TransferableRange's data from
        transferable: The associated OutgoingTransferable django model instance

    """

    transferable_range_id = uuid.uuid4()
    file_obj = cast(BinaryIO, stream_partition)

    transferable_range = models.TransferableRange(
        id=transferable_range_id,
        outgoing_transferable=transferable,
        byte_offset=transferable.bytes_received,
    )

    if not _storage_exists(transferable_range):
        __create_storage_folder(transferable_range)

    fs.append_bytes(transferable_range, file_obj.read())

    transferable_range.size = stream_partition.bytes_read
    transferable.bytes_received += transferable_range.size
    transferable.save(update_fields=["bytes_received", "size"])
    transferable_range.save()


def _finalize_transferable(
    transferable: models.OutgoingTransferable, digest: "hashlib._Hash"
) -> None:
    """Mark the transferable as successfully submitted and save the hash of the file."""
    transferable.sha1 = digest.digest()
    transferable.submission_succeeded_at = timezone.now()

    updated_fields = ["sha1", "submission_succeeded_at"]

    if transferable.size is None:
        transferable.size = transferable.bytes_received
        updated_fields.append("size")

    transferable.save(update_fields=updated_fields)


@transaction.atomic
def _perform_create_empty_transferable_range(
    transferable: models.OutgoingTransferable,
) -> None:
    """Create a transferable range of size 0 in the database and in the filesystem."""
    empty_partition = utils.StreamPartition(lambda *args: b"", 0, b"")
    _store_transferable_range(empty_partition, transferable)
    _finalize_transferable(transferable, _hash_func())


def _perform_create_transferable_ranges(
    transferable: models.OutgoingTransferable,
    stream: io.BytesIO,
) -> None:
    """Create a sequence of transferable ranges from the provided stream."""
    digest = _hash_func()

    stream_partitions = iter(
        utils.PartitionedStream(
            stream,
            settings.TRANSFERABLE_RANGE_SIZE,
            digest.update,
        )
    )

    try:
        partition = next(stream_partitions)
    except StopIteration:
        if transferable.size:
            raise exceptions.InconsistentContentLengthError(
                read=0, expected=transferable.size
            )

        return _perform_create_empty_transferable_range(transferable)

    while True:
        # ensure the creation of a transferable range and the update of the associated
        # outgoing transferable happen atomically
        with transaction.atomic():
            _store_transferable_range(partition, transferable)

            if (
                transferable.size is not None
                and transferable.bytes_received > transferable.size
            ):
                raise exceptions.InconsistentContentLengthError(
                    read=transferable.bytes_received, expected=transferable.size
                )

            if transferable.bytes_received > settings.TRANSFERABLE_MAX_SIZE:
                raise exceptions.RequestEntityTooLargeError

            try:
                partition = next(stream_partitions)
            except StopIteration:
                if (
                    transferable.size is not None
                    and transferable.bytes_received != transferable.size
                ):
                    raise exceptions.InconsistentContentLengthError(
                        read=transferable.bytes_received, expected=transferable.size
                    )

                _finalize_transferable(transferable, digest)

                break


def _revoke_transferable_unexpected_exception(
    transferable: models.OutgoingTransferable,
) -> None:
    """Create a Transferable revocation with reason UNEXPECTED_EXCEPTION.

    Args:
        transferable: the transferable that caused the issue.

    """
    models.TransferableRevocation.objects.create(
        outgoing_transferable=transferable,
        reason=enums.TransferableRevocationReason.UNEXPECTED_EXCEPTION,
    )


def _revoke_transferable_upload_size_mismatch(
    transferable: models.OutgoingTransferable,
) -> None:
    """
    Create a Transferable revocation with reason UPLOAD_SIZE_MISMATCH.

    Args:
        transferable: the transferable that caused the issue.

    """
    models.TransferableRevocation.objects.create(
        outgoing_transferable=transferable,
        reason=enums.TransferableRevocationReason.UPLOAD_SIZE_MISMATCH,
    )


def _create_transferable_ranges(
    stream: Optional[io.BytesIO],
    transferable: models.OutgoingTransferable,
) -> None:
    """
    Create TransferableRanges and update Transferable progressively.

    Write TransferableRange's data to filesystem and save to DB.
    Creates an empty TransferableRange with corresponding empty
    file if stream is None.

    Args:
        stream: the stream to read the OutgoingTransferable from
        transferable: The associated OutgoingTransferable django model instance

    """
    if stream is None:
        _perform_create_empty_transferable_range(transferable)
    else:
        _perform_create_transferable_ranges(transferable, stream)


def _create_transferable(request: drf_request.Request) -> models.OutgoingTransferable:
    """Create many TransferableRanges from the request body and return the
    saved and instantiated OutgoingTransferable django model.

    Args:
        request: The DRF Request object from which to create the Transferable

    Returns:
        The instantiated Django model for the saved OutgoingTransferable as well as the
        instantiated Django models for the associated TransferableRanges

    Raises:
        exceptions.InconsistentContentLengthError: raise this exception in case of
            mismatch between the user provided Content-Length header and the size of the
            transferable.
        exceptions.TransferableNotSuccessfullySubmittedError: raise this exception
            if the submission for this Transferable's ranges is not over at the end of
            the process.

    """
    stream = _get_body_stream(request)
    content_length = _get_content_length(request)
    user_provided_meta = utils.extract_metadata_from_headers(request.headers)
    filename = request.headers.get("metadata-name") or ""

    # the user should be authenticated
    user = cast(models.User, request.user)

    logger.debug("Create OutgoingTransferable database object.")
    transferable: models.OutgoingTransferable = (
        models.OutgoingTransferable.objects.create(
            user_profile=user.user_profile,  # type: ignore
            user_provided_meta=user_provided_meta,
            name=filename,
            size=content_length,
        )
    )

    logger.debug("Start writing file to fs.")
    try:
        _create_transferable_ranges(stream, transferable)
    except exceptions.InconsistentContentLengthError:
        # When cancelling an upload from the frontend we start by creating a
        # revocation then we abort the transfer. Thus if we reach this point
        # and we encounter a USER_CANCELED revocation, this is not an error:
        # the user is currently aborting right after having cancelled.
        revocations = models.TransferableRevocation.objects.filter(
            outgoing_transferable=transferable
        )
        if (revocations.count() != 1) or (
            revocations.get().reason != enums.TransferableRevocationReason.USER_CANCELED
        ):
            _revoke_transferable_upload_size_mismatch(transferable)
        raise
    except Exception:
        _revoke_transferable_unexpected_exception(transferable)
        raise
    logger.debug("File successfully saved.")

    if not transferable.submission_succeeded:
        raise exceptions.TransferableNotSuccessfullySubmittedError

    logger.debug("Save OutgoingTransferable database object.")
    return models.OutgoingTransferable.objects.get(id=transferable.id)


def _get_body_stream(request: drf_request.Request) -> io.BytesIO:
    """Get a file-like object to read the body of the HTTP request from.

    Args:
        request: The DRF request object corresponding to the request.

    Returns:
        A file-like object to stream read the body of the request.

    """
    if request.headers.get("Transfer-Encoding") == "chunked":
        # Read the HTTP request body directly using the WSGI object provided by
        # the server. This is required to handle requests using chunked transfer
        # encoding, as HTTP requests with no Content-Length set are not passed
        # to Django.
        #
        # Note: A server supporting chunked transfer encoding, such as Gunicorn,
        # is required.
        return request.META["wsgi.input"]  # pragma: no cover

    return request.stream


def _get_content_length(request: drf_request.Request) -> Optional[int]:
    """Attempt to check the `Content-Length` header against the configured
    maximum Transferable size and return it.

    Args:
        request: the request to check.

    Raises:
        InvalidContentLengthError: if the `Content-Length` value cannot be parsed
            as an integer.
        RequestEntityTooLargeError: if the `Content-Length` value is too big.

    Returns:
        Checked content length.

    """
    if request.headers.get("Transfer-Encoding") == "chunked":
        # The 'Content-Length' header should be omitted when the 'Transfer-Encoding'
        # header is set to 'chunked'.
        # See: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Transfer-Encoding#directives  # noqa: E501
        logger.warning(
            "Cannot retrieve the 'Content-Length' header of an HTTP request "
            "using chunked transfer encoding."
        )
        return None

    try:
        content_length = request.headers["Content-Length"]
    except KeyError:
        return None

    if content_length == "":
        return None

    try:
        content_length = int(content_length)
    except ValueError:
        raise exceptions.InvalidContentLengthError

    if content_length < 0:
        return None

    if content_length > settings.TRANSFERABLE_MAX_SIZE:
        raise exceptions.RequestEntityTooLargeError

    return content_length


def _ensure_content_type_is_octet_stream(request: drf_request.Request) -> None:
    """Checks that the Content-Type header value of the request is
    'application/octet-stream'.

    NOTE: This check exists because, for some reason, DRF's parsers are ignored
          on the OutgoingTransferable view when using DRF's TokenAuthentication.

    Raises:
        exceptions.MissingContentTypeError if there is no Content-Type header
        drf_exceptions.UnsupportedMediaType if the value of the
        Content-Type header is not 'application/octet-stream'.

    """
    try:
        content_type = request.headers["Content-Type"]
    except KeyError:
        raise exceptions.MissingContentTypeError

    if content_type != "application/octet-stream":
        raise drf_exceptions.UnsupportedMediaType(content_type)


@documentation.outgoing_transferable
# NOTE: this makes all views in the viewset use non atomic requests
# see: https://stackoverflow.com/a/49903525 and https://stackoverflow.com/a/44596892
@decorators.method_decorator(transaction.non_atomic_requests, name="dispatch")
class OutgoingTransferableViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
):
    """
    Viewset to list and retrieve OutgoingTransferables which also
    implements a create method for uploading file content in body.
    """

    serializer_class = serializers.OutgoingTransferableSerializer
    queryset = models.OutgoingTransferable.objects.all()
    pagination_class = pagination.EurydiceSessionPagination
    permission_classes = [permissions.IsTransferableOwner]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = origin_filters.OutgoingTransferableFilter
    parser_classes = [parsers.OctetStreamParser]
    throttle_scope = "create_transferable"

    def get_queryset(self) -> query.QuerySet:
        """Filter queryset to only retrieve OutgoingTransferables for the current user.

        Returns:
            filtered queryset

        """
        queryset = super().get_queryset()
        return queryset.filter(user_profile__user__id=self.request.user.id).order_by(
            "-created_at"
        )

    def get_throttles(self) -> List[throttling.BaseThrottle]:
        """Instantiates and returns the list of throttles that this view uses."""
        if self.action == "create":
            throttle_classes = [throttling.ScopedRateThrottle]
        else:
            throttle_classes = []  # No throttle for other actions
        return [throttle() for throttle in throttle_classes]

    def create(
        self, request: drf_request.Request, *args, **kwargs
    ) -> drf_response.Response:
        """Create a transferable and upload its content."""
        _ensure_content_type_is_octet_stream(request)
        transferable = _create_transferable(request)

        serializer = self.get_serializer(transferable)
        return drf_response.Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(
        self, request: drf_request.Request, *args, **kwargs
    ) -> drf_response.Response:
        """Revoke a transferable waiting to be or being transferred."""
        instance = self.get_object()

        logger.debug("Create TransferableRevocation database object.")
        models.TransferableRevocation.objects.create(
            outgoing_transferable=instance,
            reason=enums.TransferableRevocationReason.USER_CANCELED,
        )

        logger.debug("Save TransferableRevocation database object.")
        return drf_response.Response(status=status.HTTP_204_NO_CONTENT)
