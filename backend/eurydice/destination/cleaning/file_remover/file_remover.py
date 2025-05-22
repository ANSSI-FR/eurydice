import logging
from typing import Iterator

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from eurydice.common.cleaning.repeated_task import RepeatedTask
from eurydice.destination.core import models
from eurydice.destination.storage import fs

logging.config.dictConfig(settings.LOGGING)  # type: ignore
logger = logging.getLogger(__name__)


class DestinationFileRemover(RepeatedTask):
    """Removes old files on the filesystem storage folder.
    Files from successful IncomingTransferables that finished
    `settings.FILE_REMOVER_EXPIRE_TRANSFERABLES_AFTER` ago will be removed.
    The removal frequency is defined by `settings.FILE_REMOVER_RUN_EVERY` and
    `settings.FILE_REMOVER_POLL_EVERY`.
    """

    def __init__(self) -> None:
        super().__init__(
            settings.FILE_REMOVER_RUN_EVERY, settings.FILE_REMOVER_POLL_EVERY
        )

    def _ready(self) -> None:
        """Logs that the File Remover is ready before first loop."""
        logger.info("Ready")

    def _select_transferables_to_remove(self) -> Iterator[models.IncomingTransferable]:
        """List successful transferables that have expired."""
        expiration_time = (
            timezone.now() - settings.FILE_REMOVER_EXPIRE_TRANSFERABLES_AFTER
        )
        qset = models.IncomingTransferable.objects.filter(
            state=models.IncomingTransferableState.SUCCESS,
            finished_at__lt=expiration_time,
        ).union(
            models.IncomingTransferable.objects.filter(
                state=models.IncomingTransferableState.ONGOING,
                created_at__lt=expiration_time,
            ).exclude(file_upload_parts__created_at__gte=expiration_time)
        )
        return qset.iterator()

    def _remove_transferable(self, transferable: models.IncomingTransferable) -> None:
        """Mark the provided transferable as EXPIRED and remove its data from the
        storage.
        """
        with transaction.atomic():
            if transferable.state == models.IncomingTransferableState.ONGOING:
                transferable.mark_as_error()
                target_status = models.IncomingTransferableState.ERROR
            else:
                transferable.mark_as_expired()
                target_status = models.IncomingTransferableState.EXPIRED

            fs.delete(transferable)

        logger.info(
            f"The IncomingTransferable {transferable.id} has been marked as "
            f"{target_status.value}, "  # pytype: disable=attribute-error
            f"and its data removed from the storage."
        )

    def _run(self) -> None:
        """Process SUCCESS transferables to expire."""
        for transferable in self._select_transferables_to_remove():
            self._remove_transferable(transferable)
