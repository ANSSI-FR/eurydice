import collections
import logging
import uuid
from typing import Dict
from typing import Set

from django.conf import settings
from django.utils import timezone

from eurydice.common import protocol
from eurydice.destination.core import models
from eurydice.destination.receiver.packet_handler import s3_helpers
from eurydice.destination.receiver.packet_handler.extractors import base
from eurydice.destination.storage import fs

UUIDSet = Set[uuid.UUID]

logger = logging.getLogger(__name__)


class _HistoryEntryMap(collections.UserDict):
    """A convenient representation of a History object that maps transferable IDs
    to HistoryEntries.

    Args:
        history: the History object to convert to a mapping.

    """

    def __init__(self, history: protocol.History) -> None:
        super().__init__()
        self.data: Dict[uuid.UUID, protocol.HistoryEntry] = {
            e.transferable_id: e for e in history.entries
        }


def _filter(transferable_ids: UUIDSet, **kwargs) -> UUIDSet:
    """Select the `transferable_ids` corresponding to IncomingTransferables in
    the database using, in addition, filter parameters provided as kwargs."""
    results = models.IncomingTransferable.objects.filter(
        id__in=transferable_ids, **kwargs
    ).values_list("id", flat=True)

    return set(results)  # type: ignore


def _list_ongoing_transferable_ids(transferable_ids: UUIDSet) -> UUIDSet:
    """Select the IncomingTransferable that have their id in `transferable_ids` and
    that have the state ONGOING.
    """
    return _filter(transferable_ids, state=models.IncomingTransferableState.ONGOING)


def _list_finished_transferable_ids(transferable_ids: UUIDSet) -> UUIDSet:
    """Select the IncomingTransferable that have their id in `transferable_ids` and
    that have been completely processed (i.e. with a final state).
    """
    return _filter(
        transferable_ids, state__in=models.IncomingTransferableState.get_final_states()
    )


def _list_missed_transferable_ids(
    all_transferable_ids: UUIDSet, ongoing_transferable_ids: UUIDSet
) -> UUIDSet:
    """Select the IncomingTransferable that have their id in `all_transferable_ids`
    and that do not appear in the database.
    """
    finished_transferables_ids = _list_finished_transferable_ids(all_transferable_ids)
    return all_transferable_ids - ongoing_transferable_ids - finished_transferables_ids


def _process_ongoing_transferables(ongoing_transferable_ids: UUIDSet) -> None:
    """Abort the multipart uploads of the ONGOING transferables and mark the objects
    as ERROR.
    """
    for transferable_id in ongoing_transferable_ids:
        transferable = models.IncomingTransferable.objects.get(id=transferable_id)
        if settings.MINIO_ENABLED:
            s3_helpers.abort_multipart_upload(transferable)
        else:
            fs.delete(transferable)
        transferable.mark_as_error()

        logger.error(
            f"According to history, transferable '{transferable.id}' is in a "
            f"final state, but it was not the case receiver-side: marked this transfer "
            f"as failure and removed its parts from storage (if it had any)."
        )


def _process_missed_transferables(
    missed_transferable_ids: UUIDSet, history_entry_map: _HistoryEntryMap
) -> None:
    """Create IncomingTransferable ERROR entries in the database to record transferables
    that did not reach the destination side.
    """
    for missed_id in missed_transferable_ids:
        user_profile, _ = models.UserProfile.objects.get_or_create(
            associated_user_profile_id=history_entry_map[missed_id].user_profile_id
        )

        now = timezone.now()
        models.IncomingTransferable.objects.create(
            id=missed_id,
            name=history_entry_map[missed_id].name,
            sha1=history_entry_map[missed_id].sha1,
            bytes_received=0,
            size=None,
            s3_bucket_name="",
            s3_object_name="",
            s3_upload_id="",
            user_profile=user_profile,
            user_provided_meta=history_entry_map[missed_id].user_provided_meta or {},
            created_at=now,
            finished_at=now,
            state=models.IncomingTransferableState.ERROR,
        )

        logger.info(
            f"The IncomingTransferable {missed_id} has been created in database "
            f"with the state ERROR."
        )


def _process_history(history: protocol.History) -> None:
    """Abort ONGOING IncomingTransferable that appear in the history and record in the
    database transferables that did not reach the destination side.
    """
    history_entry_map = _HistoryEntryMap(history)
    transferable_ids = set(history_entry_map.keys())

    ongoing_transferable_ids = _list_ongoing_transferable_ids(transferable_ids)
    missed_transferable_ids = _list_missed_transferable_ids(
        transferable_ids, ongoing_transferable_ids
    )

    _process_ongoing_transferables(ongoing_transferable_ids)
    _process_missed_transferables(missed_transferable_ids, history_entry_map)


class OngoingHistoryExtractor(base.OnTheWirePacketExtractor):
    """Process the history packaged in an OnTheWirePacket."""

    def extract(self, packet: protocol.OnTheWirePacket) -> None:
        """Entrypoint of the OnTheWirePacketExtractor. Process the history in an
        OnTheWirePacket if there is one.

        Args:
            packet: the OnTheWirePacket containing the history to process.

        """
        if packet.history:
            logger.debug("Start processing history.")
            _process_history(packet.history)
            logger.info("History processed.")


__all__ = ("OngoingHistoryExtractor",)
