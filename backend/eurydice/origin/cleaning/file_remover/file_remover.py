import contextlib
from typing import Iterator

from django.conf import settings
from django.db import IntegrityError
from django.utils import timezone

from eurydice.common import enums
from eurydice.common.cleaning.repeated_task import RepeatedTask
from eurydice.common.logging.logger import LOG_KEY, logger
from eurydice.origin.api.views.outgoing_transferable import get_transferable_file_path
from eurydice.origin.core import models


class OriginFileRemover(RepeatedTask):
    """Removes old files on the filesystem storage folder.
    Files from successful OutgoingTransferables that finished
    `settings.FILE_REMOVER_EXPIRE_TRANSFERABLES_AFTER` ago will be removed.
    The removal frequency is defined by `settings.FILE_REMOVER_RUN_EVERY` and
    `settings.FILE_REMOVER_POLL_EVERY`.
    """

    def __init__(self) -> None:
        super().__init__(settings.FILE_REMOVER_RUN_EVERY, settings.FILE_REMOVER_POLL_EVERY)

    def _ready(self) -> None:
        """Logs that the File Remover is ready before first loop."""
        logger.info({LOG_KEY: "file_remover_origin", "status": "ready"})

    def _select_transferables_to_remove(self) -> Iterator[models.OutgoingTransferable]:
        """List successful transferables that have expired."""
        expiration_time = timezone.now() - settings.FILE_REMOVER_EXPIRE_TRANSFERABLES_AFTER

        # These files still potentially have temporary files associated
        # from multipart upload interruption
        to_delete_states = [
            enums.OutgoingTransferableState.ERROR,
            enums.OutgoingTransferableState.PENDING,
        ]

        to_delete = models.OutgoingTransferable.objects.filter(
            state__in=to_delete_states,  # type: ignore
            created_at__lt=expiration_time,
        )
        return to_delete.iterator()

    def _remove_transferable(self, transferable: models.OutgoingTransferable) -> None:
        """Mark the provided transferable as CANCELED and remove its data from the
        storage.
        """
        with contextlib.suppress(IntegrityError):
            models.TransferableRevocation.objects.update_or_create(
                outgoing_transferable=transferable,
                reason=enums.TransferableRevocationReason.UPLOAD_INTERRUPTION,
            )

        target_file_path = get_transferable_file_path(str(transferable.id))

        if target_file_path.exists():
            target_file_path.unlink(missing_ok=True)

    def _run(self) -> None:
        """Process SUCCESS transferables to expire."""
        logger.info({LOG_KEY: "file_remover_origin", "status": "start"})
        for transferable in self._select_transferables_to_remove():
            self._remove_transferable(transferable)

        logger.info({LOG_KEY: "file_remover_origin", "status": "done"})
