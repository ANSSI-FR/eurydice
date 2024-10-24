import hashlib
import io
import logging
from typing import NamedTuple

from django.db import transaction

from eurydice.common import minio
from eurydice.destination.core import models
from eurydice.destination.receiver.packet_handler import s3_helpers
from eurydice.destination.utils import rehash

logger = logging.getLogger(__name__)


class PendingIngestionData(NamedTuple):
    """
    Data ready to be ingested into a Transferable.

    Attributes:
        data: data to be ingested into the Transferable.
        sha1: cumulative SHA1 of current data and all data previously ingested into
            the Transferable.
        eof: boolean indicating whether or not the end of the Transferable has been
            reached (if false, additional data should come later).
    """

    data: bytes
    sha1: "hashlib._Hash"
    eof: bool


def _store_single_range(
    incoming_transferable: models.IncomingTransferable,
    data: bytes,
) -> None:
    """
    Add data to the file storage as a direct upload (no Multi-Part Upload).
    """
    logger.debug("Start uploading full object to MinIO.")
    minio.client.put_object(
        bucket_name=incoming_transferable.s3_bucket_name,
        object_name=incoming_transferable.s3_object_name,
        data=io.BytesIO(data),
        length=len(data),
    )
    logger.debug("Full object successfully uploaded to MinIO.")


def _start_multipart_upload(incoming_transferable: models.IncomingTransferable) -> None:
    """
    Initiate a Multi-Part Upload (without data yet).
    """
    incoming_transferable.s3_upload_id = s3_helpers.initiate_multipart_upload(
        incoming_transferable
    )
    incoming_transferable.save(update_fields=["s3_upload_id"])


def _get_next_part_number(incoming_transferable: models.IncomingTransferable) -> int:
    """
    Calculate the number of the next Multi-Part Upload to perform on given Transferable.
    """
    return (
        models.S3UploadPart.objects.filter(
            incoming_transferable=incoming_transferable
        ).count()
        + 1
    )


def _store_range(
    incoming_transferable: models.IncomingTransferable,
    data: bytes,
) -> None:
    """
    Add data to an existing Multi-Part Upload.
    """
    s3_part_number = _get_next_part_number(incoming_transferable)

    logger.debug("Start uploading object part to MinIO.")
    # NOTE: if the next part takes more than 24 hours to arrive, the multipart upload
    # will have been purged by minio
    # https://github.com/minio/minio/blob/c0e79e28b25da4212467d1d7ecc767e732f384c2/cmd/fs-v1-multipart.go#L887
    part_upload_result = minio.client._upload_part(
        bucket_name=incoming_transferable.s3_bucket_name,
        object_name=incoming_transferable.s3_object_name,
        data=data,
        headers={},
        upload_id=incoming_transferable.s3_upload_id,
        part_number=s3_part_number,
    )
    logger.debug("Object part successfully uploaded to MinIO.")

    logger.debug("Create S3UploadPart object in database.")
    models.S3UploadPart.objects.create(
        etag=bytes.fromhex(part_upload_result),
        incoming_transferable=incoming_transferable,
        part_number=s3_part_number,
    )


def _update_incoming_transferable(
    incoming_transferable: models.IncomingTransferable,
    to_ingest: PendingIngestionData,
) -> None:
    """
    Registers new data to the Transferable database entry, but does not send actual data
    to the S3 file storage (this is done in above functions).

    Args:
        incoming_transferable: Transferable to update.
        to_ingest: PendingIngestionData to ingest into the IncomingTransferable.
    """
    incoming_transferable.bytes_received += len(to_ingest.data)
    incoming_transferable.rehash_intermediary = rehash.sha1_to_bytes(to_ingest.sha1)

    updated_fields = ["bytes_received", "rehash_intermediary"]

    if to_ingest.eof:
        incoming_transferable.size = incoming_transferable.bytes_received
        incoming_transferable.sha1 = to_ingest.sha1.digest()
        incoming_transferable.mark_as_success(save=False)
        updated_fields.extend(("size", "state", "finished_at", "sha1"))

    incoming_transferable.save(update_fields=updated_fields)


def ingest(
    incoming_transferable: models.IncomingTransferable,
    to_ingest: PendingIngestionData,
) -> None:
    """
    Add data to the given Transferable.

    Args:
        incoming_transferable: Transferable to add data to.
        to_ingest: PendingIngestionData to ingest into the IncomingTransferable.
    """
    if to_ingest.eof and not incoming_transferable.s3_upload_id:
        with transaction.atomic():
            _update_incoming_transferable(incoming_transferable, to_ingest)
            _store_single_range(incoming_transferable, to_ingest.data)
    else:
        if not incoming_transferable.s3_upload_id:
            _start_multipart_upload(incoming_transferable)

        with transaction.atomic():
            _update_incoming_transferable(incoming_transferable, to_ingest)

            _store_range(incoming_transferable, to_ingest.data)
            if to_ingest.eof:
                s3_helpers.complete_multipart_upload(incoming_transferable)


def abort_ingestion(failed_transferable: models.IncomingTransferable) -> None:
    """
    Abort a Transferable ingestion. This will mark the Transferable as ERROR, and
    delete all associated data from the object storage.

    Args:
        failed_transferable: Transferable that failed (its data will be deleted).
    """
    s3_helpers.abort_multipart_upload(failed_transferable)
    failed_transferable.mark_as_error()


__all__ = ["PendingIngestionData", "ingest", "abort_ingestion"]
