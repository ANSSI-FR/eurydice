from datetime import datetime

from django.conf import settings
from django.utils import timezone

from eurydice.common.cleaning import repeated_task
from eurydice.common.enums import OutgoingTransferableState
from eurydice.common.logging.logger import LOG_KEY, logger
from eurydice.origin.core import models

BULK_DELETION_SIZE = 65_536


class OriginDBTrimmer(repeated_task.RepeatedTask):
    """Removes old IncomingTransferables from the database.
    Expired IncomingTransferables that finished
    `settings.DBTRIMMER_TRIM_TRANSFERABLES_AFTER` ago will be removed.
    The removal frequency is defined by `settings.DBTRIMMER_RUN_EVERY` and
    `settings.DBTRIMMER_POLL_EVERY`.
    """

    def __init__(self) -> None:
        super().__init__(settings.DBTRIMMER_RUN_EVERY, settings.DBTRIMMER_POLL_EVERY)

    def _ready(self) -> None:
        """Logs that the OriginDBTrimmer is ready before first loop."""
        logger.info({LOG_KEY: "db_trimmer_origin", "status": "ready"})

    def _run(self) -> None:
        """Delete old transferables in a final state.

        It is safe to remove the OutgoingTransferables in a final state,
        since transaction atomicity guaranties their associated files do not
        exist anymore."""
        logger.info({LOG_KEY: "db_trimmer_origin", "status": "running"})

        remove_created_before = timezone.now() - settings.DBTRIMMER_TRIM_TRANSFERABLES_AFTER

        finished = False
        while not finished:
            finished = self.trim_bulk(remove_created_before)

        logger.info({LOG_KEY: "db_trimmer_origin", "status": "done"})

    def trim_bulk(self, remove_created_before: datetime) -> bool:
        """Delete a bulk of old transferables in a final state.

        Bulk size is specified in the BULK_DELETION_SIZE variable. Since Django
        retrieves TransferableRanges to delete them before deleting
        OutgoingTransferables and does not clean memory as it does, it is better to
        keep this value quite low to avoid excessive memory consumption.

        This function can be called in a loop as long as it returns True, meaning
        transferables were successfully deleted.
        """
        to_delete = models.OutgoingTransferable.objects.filter(  # type: ignore[misc]
            state__in=OutgoingTransferableState.get_final_states(),
            created_at__lt=remove_created_before,
        )[:BULK_DELETION_SIZE].values_list("id", flat=True)

        delete_count = len(to_delete)
        if delete_count == 0:
            return True

        logger.info(
            {
                LOG_KEY: "db_trimmer_origin",
                "message": "DBTrimmer will remove OutgoingTransferables and all associated objects.",
                "outgoing_transferables_count": delete_count,
            }
        )

        # Django will implicitly split the to_delete list into blocks
        # of 100 IDs each, but this seems unavoidable :
        # https://code.djangoproject.com/ticket/9519
        _, deletions_by_class = models.OutgoingTransferable.objects.filter(id__in=to_delete).delete()

        deleted_ranges = deletions_by_class.get("eurydice_origin_core.TransferableRange", 0)
        deleted_revocations = deletions_by_class.get("eurydice_origin_core.TransferableRevocation", 0)
        deleted_transferables = deletions_by_class.get("eurydice_origin_core.OutgoingTransferable", 0)

        logger.info(
            {
                LOG_KEY: "db_trimmer_origin",
                "message": "DBTrimmer finished successfully",
                "deleted_transferables": deleted_transferables,
                "deleted_ranges": deleted_ranges,
                "deleted_revocations": deleted_revocations,
            }
        )

        if deleted_transferables != delete_count:
            logger.error(
                {
                    LOG_KEY: "db_trimmer_origin",
                    "message": "DBTrimmer deletion mismatch",
                    "deleted_transferables": deleted_transferables,
                    "expected_deleted_transferables": delete_count,
                }
            )
            return True

        return False
