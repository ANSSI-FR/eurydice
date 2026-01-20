from typing import Iterator

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from eurydice.common.cleaning.repeated_task import RepeatedTask
from eurydice.common.logging.logger import LOG_KEY, logger
from eurydice.destination.core import models
from eurydice.destination.storage import fs


class DestinationFileRemover(RepeatedTask):
    """Removes old files on the filesystem storage folder.
    Files from successful IncomingTransferables that finished
    `settings.FILE_REMOVER_EXPIRE_TRANSFERABLES_AFTER` ago will be removed.
    The removal frequency is defined by `settings.FILE_REMOVER_RUN_EVERY` and
    `settings.FILE_REMOVER_POLL_EVERY`.
    """

    def __init__(self) -> None:
        super().__init__(settings.FILE_REMOVER_RUN_EVERY, settings.FILE_REMOVER_POLL_EVERY)

    def _ready(self) -> None:
        """Logs that the File Remover is ready before first loop."""
        logger.info({LOG_KEY: "file_remover_destination", "status": "ready"})

    def _select_transferables_to_remove(self) -> Iterator[models.IncomingTransferable]:
        """List successful transferables that have expired."""
        expiration_time = timezone.now() - settings.FILE_REMOVER_EXPIRE_TRANSFERABLES_AFTER
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
            {
                LOG_KEY: "file_remover_destination",
                "status": target_status.value,
                "transferable_id": str(transferable.id),
                "message": "Transferable status updated and data removed from fs",
            }
        )

    def _run(self) -> None:
        """Process SUCCESS transferables to expire."""
        for transferable in self._select_transferables_to_remove():
            self._remove_transferable(transferable)
