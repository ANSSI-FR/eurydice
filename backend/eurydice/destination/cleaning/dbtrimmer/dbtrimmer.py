import logging
from datetime import datetime

from django.conf import settings
from django.utils import timezone

from eurydice.common.cleaning import repeated_task
from eurydice.destination.core import models

logging.config.dictConfig(settings.LOGGING)  # type: ignore
logger = logging.getLogger(__name__)

BULK_DELETION_SIZE = 65_536


class DestinationDBTrimmer(repeated_task.RepeatedTask):
    """Removes old IncomingTransferables from the database.
    Expired IncomingTransferables that finished
    `settings.DBTRIMMER_TRIM_TRANSFERABLES_AFTER` ago will be removed.
    The removal frequency is defined by `settings.DBTRIMMER_RUN_EVERY` and
    `settings.DBTRIMMER_POLL_EVERY`.
    """

    def __init__(self) -> None:
        super().__init__(settings.DBTRIMMER_RUN_EVERY, settings.DBTRIMMER_POLL_EVERY)

    def _ready(self) -> None:
        """Logs that the DestinationDBTrimmer is ready before first loop."""
        logger.info("Ready")

    def _run(self) -> None:
        """Delete old transferables in a final state.

        Final states are ERROR, EXPIRED, REMOVED and REVOKED.
        It is safe to remove the IncomingTransferables in the states listed above,
        since transaction atomicity guaranties their associated S3 objects do not
        exist anymore.
        """
        logger.info("DBTrimmer is running")

        remove_finished_before = (
            timezone.now() - settings.DBTRIMMER_TRIM_TRANSFERABLES_AFTER
        )

        finished = False
        while not finished:
            finished = self.trim_bulk(remove_finished_before)

        logger.info("DBTrimmer finished running")

    def trim_bulk(self, remove_finished_before: datetime) -> bool:
        """Delete a bulk of old transferables in a final state.

        Bulk size is specified in the BULK_DELETION_SIZE variable. Since Django
        retrieves TransferableRanges to delete them before deleting
        OutgoingTransferables and does not clean memory as it does, it is better to
        keep this value quite low to avoid excessive memory consumption.

        This function can be called in a loop as long as it returns True, meaning
        transferables were successfully deleted.
        """

        to_delete = models.IncomingTransferable.objects.filter(
            state__in=[
                models.IncomingTransferableState.ERROR,
                models.IncomingTransferableState.EXPIRED,
                models.IncomingTransferableState.REMOVED,
                models.IncomingTransferableState.REVOKED,
            ],
            finished_at__lt=remove_finished_before,
        )[:BULK_DELETION_SIZE].values_list("id", flat=True)

        delete_count = len(to_delete)
        if delete_count == 0:
            return True

        logger.info(f"DBTrimmer will remove {delete_count} entries.")

        # Django will implicitly split the to_delete list into blocks
        # of 100 IDs each, but this seems unavoidable :
        # https://code.djangoproject.com/ticket/9519
        total_deletions, _ = models.IncomingTransferable.objects.filter(
            id__in=to_delete
        ).delete()

        logger.info(f"DBTrimmer successfully removed {total_deletions} entries.")

        if total_deletions != delete_count:
            logger.error(
                f"DBTrimmer deleted {total_deletions} entries, "
                f"instead of the expected {delete_count}."
            )
            return True

        return False
