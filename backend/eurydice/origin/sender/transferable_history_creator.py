import datetime

from django.conf import settings
from django.db.models.query import QuerySet
from django.utils import timezone

import eurydice.common.enums as enums
import eurydice.common.protocol as protocol
import eurydice.origin.core.models as models
from eurydice.common.logging.logger import LOG_KEY, logger


def _build_history_entries(
    outgoing_transferables: QuerySet[models.OutgoingTransferable],
) -> list[protocol.HistoryEntry]:
    """
    Given an OutgoingTransferable queryset, create and return HistoryEntries

    Args:
        outgoing_transferables: OutgoingTransferables queryset to build history entries

    Returns:
        HistoryEntries for the given OutgoingTransferables
    """
    return [
        protocol.HistoryEntry(
            transferable_id=transferable.id,
            user_profile_id=transferable.user_profile.id,
            # state is annotated
            state=transferable.state,  # type: ignore
            name=transferable.name,
            sha1=None if not transferable.sha1 else bytes(transferable.sha1),
            user_provided_meta=transferable.user_provided_meta,
        )
        for transferable in outgoing_transferables
    ]


class TransferableHistoryCreator:
    """
    Allows for the generation of OutgoingTransferable Histories.
    """

    def __init__(self) -> None:
        self._previous_history_generated_at: datetime.datetime | None = None
        self._send_every = datetime.timedelta(seconds=settings.TRANSFERABLE_HISTORY_SEND_EVERY)
        self._history_duration = datetime.timedelta(seconds=settings.TRANSFERABLE_HISTORY_DURATION)

    def too_soon(self, now: datetime.datetime) -> bool:
        """
        Given a timestamp, return True if it is too soon to generate another History,
        False otherwise

        Args:
            now: timestamp to evaluate

        Returns:
            True if too soon, False otherwise
        """
        return (
            self._previous_history_generated_at is not None
            and now - self._previous_history_generated_at < self._send_every
        )

    def get_next_history(self) -> protocol.History | None:
        """
        Returns the next OutgoingTransferable history if enough time has
        passed since the last one.

        Returns:
            the built History or None if previous History is too recent
        """

        now = timezone.now()

        if self.too_soon(now):
            return None

        min_updated_at_date = now - self._history_duration

        logger.info({LOG_KEY: "history_generation_start"})
        outgoing_transferables = models.OutgoingTransferable.objects_with_state_only.filter(  # type: ignore
            state__in=enums.OutgoingTransferableState.get_final_states(),
            auto_state_updated_at__gte=min_updated_at_date,
        ).only("id", "user_profile_id", "name", "sha1")

        history = protocol.History(entries=_build_history_entries(outgoing_transferables))
        logger.info({LOG_KEY: "history_generation_end"})

        self._previous_history_generated_at = now

        return history


__all__ = ("TransferableHistoryCreator",)
