import hashlib
from math import ceil
from typing import NamedTuple

from django.db import transaction

from eurydice.common.logging.logger import LOG_KEY, logger
from eurydice.destination.core import models
from eurydice.destination.storage import fs
from eurydice.destination.utils import rehash


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


def _storage_exists(incoming_transferable: models.IncomingTransferable) -> bool:
    return fs.file_path(incoming_transferable).is_file()


def _create_storage_file(incoming_transferable: models.IncomingTransferable) -> None:
    """
    Initiate a Multi-Part Upload (without data yet).
    """
    file_path = fs.file_path(incoming_transferable)
    logger.info(
        {
            LOG_KEY: "create_storage_file",
            "status": "starting",
            "message": "Creating empty file on filesystem for multipart upload.",
        }
    )
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.touch(exist_ok=False)

    logger.info({LOG_KEY: "create_storage_file", "status": "done"})


def _store_range(
    incoming_transferable: models.IncomingTransferable,
    data: bytes,
) -> None:
    """
    Add data to an existing Multi-Part Upload.
    """
    fs.append_bytes(incoming_transferable, data)
    logger.debug({LOG_KEY: "store_range", "status": "done"})


def _update_incoming_transferable(
    incoming_transferable: models.IncomingTransferable,
    to_ingest: PendingIngestionData,
) -> None:
    """
    Registers new data to the Transferable database entry, but does not send actual data
    to the file storage (this is done in above functions).

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
    if not _storage_exists(incoming_transferable):
        _create_storage_file(incoming_transferable)

    with transaction.atomic():
        _update_incoming_transferable(incoming_transferable, to_ingest)
        _store_range(incoming_transferable, to_ingest.data)

        # keep track of parts so that file_remover
        # can clear broken ONGOING transferables
        if not to_ingest.eof:
            logger.info(
                {
                    LOG_KEY: "ingest_destination",
                    "status": "starting",
                    "message": "Create FileUploadPart object in database.",
                }
            )
            part_number = ceil(incoming_transferable.bytes_received // len(to_ingest.data))
            models.FileUploadPart.objects.create(
                incoming_transferable=incoming_transferable,
                part_number=part_number,
            )
        else:
            incoming_transferable._clear_multipart_data()

    if to_ingest.eof:
        # _update_incoming_transferable already handles that
        pass


def abort_ingestion(failed_transferable: models.IncomingTransferable) -> None:
    """
    Abort a Transferable ingestion. This will mark the Transferable as ERROR, and
    delete all associated data from the object storage.

    Args:
        failed_transferable: Transferable that failed (its data will be deleted).
    """
    fs.delete(failed_transferable)
    failed_transferable.bytes_received = 0

    failed_transferable.mark_as_error()


__all__ = ["PendingIngestionData", "ingest", "abort_ingestion"]
