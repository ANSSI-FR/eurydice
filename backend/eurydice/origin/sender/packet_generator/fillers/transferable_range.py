from typing import Iterator

from django.conf import settings
from django.db import models
from django.db.models.query import QuerySet

import eurydice.common.protocol as protocol
import eurydice.origin.core.models as origin_models
import eurydice.origin.sender.user_selector as user_selector
from eurydice.common import exceptions
from eurydice.common.logging.logger import LOG_KEY, logger
from eurydice.common.utils import orm
from eurydice.origin.core import enums as origin_enums
from eurydice.origin.sender.packet_generator.fillers import base
from eurydice.origin.storage import fs


def _build_protocol_transferable(
    transferable_range: origin_models.TransferableRange,
) -> protocol.Transferable:
    """
    Given the django model for a TransferableRange and a user, build the
    protocol's model for the associated Transferable

    Args:
        transferable_range: the TransferableRange django model

    Returns:
        protocol's model for the associated Transferable
    """

    sha1: bytes | None = None

    if transferable_range.is_last:
        sha1 = bytes(transferable_range.outgoing_transferable.sha1)  # type: ignore[attr-defined]
    else:
        sha1 = None

    return protocol.Transferable(
        id=transferable_range.outgoing_transferable.id,  # type: ignore[attr-defined]
        name=transferable_range.outgoing_transferable.name,  # type: ignore[attr-defined]
        user_provided_meta=transferable_range.outgoing_transferable.user_provided_meta,  # type: ignore[attr-defined]  # noqa: E501
        sha1=sha1,
        size=transferable_range.outgoing_transferable.size,  # type: ignore[attr-defined]
        user_profile_id=transferable_range.outgoing_transferable.user_profile.id,  # type: ignore[attr-defined]
    )


def _fetch_next_transferable_ranges_for_user(
    user: origin_models.User,
) -> QuerySet[origin_models.TransferableRange]:
    """
    Fetch the given user's next MAX_TRANSFERABLES_PER_PACKET pending
    TransferableRanges.

    Args:
        user: for filtering TransferableRanges

    Returns:
        the user's pending TransferableRanges

    """

    return orm.make_queryset_with_subquery_join(
        queryset=origin_models.TransferableRange.objects.select_related("outgoing_transferable__revocation")
        .filter(
            outgoing_transferable__user_profile=user.user_profile,  # type: ignore
            transfer_state=origin_enums.TransferableRangeTransferState.PENDING,
        )
        .order_by("created_at"),
        subquery=origin_models.TransferableRange.objects.values("outgoing_transferable_id").filter(
            transfer_state=origin_enums.TransferableRangeTransferState.ERROR,
        ),
        on=models.Q(outgoing_transferable_id=models.F("outgoing_transferable_id")),
        select={"erroneous_outgoing_transferable_id": "outgoing_transferable_id"},
    )[: settings.MAX_TRANSFERABLES_PER_PACKET]


def _fetch_pending_transferable_ranges() -> QuerySet[origin_models.TransferableRange]:
    """
    Fetch the next MAX_TRANSFERABLES_PER_PACKET pending TransferableRanges.

    Also pre-fetches revocations and ERROR ranges, to reduce the amount of db queries.

    Returns:
        the pending TransferableRanges

    """

    return orm.make_queryset_with_subquery_join(
        queryset=origin_models.TransferableRange.objects.select_related("outgoing_transferable__revocation")
        .filter(
            transfer_state=origin_enums.TransferableRangeTransferState.PENDING,
        )
        .order_by("created_at"),
        subquery=origin_models.TransferableRange.objects.values("outgoing_transferable_id").filter(
            transfer_state=origin_enums.TransferableRangeTransferState.ERROR,
        ),
        on=models.Q(outgoing_transferable_id=models.F("outgoing_transferable_id")),
        select={"erroneous_outgoing_transferable_id": "outgoing_transferable_id"},
    )[: settings.MAX_TRANSFERABLES_PER_PACKET]


def _get_transferable_range_data(
    transferable_range: origin_models.TransferableRange,
) -> bytes:
    """
    Given a TransferableRange, fetch and return its data from the filesystem.

    Args:
        transferable_range: range for which to fetch data

    Returns:
        TransferableRange data as bytes

    Raises:
        FileNotFoundError: if object is not found in filesystem.

    """
    try:
        data = fs.read_bytes(transferable_range)
    except FileNotFoundError as e:
        raise exceptions.FileNotFoundError() from e

    return data


class OTWPacketAlreadyHasTransferableRanges(ValueError):
    """
    Exception raised when passing an OnTheWirePacket which already has
    TransferableRanges to the TransferableRangeFiller.
    """


def _delete_objects_from_fs(
    transferable_ranges: list[origin_models.TransferableRange],
) -> None:
    """
    Delete TransferableRanges data from filesystem.

    Args:
        transferable_ranges: List of TransferableRanges to delete data from fs
    """
    for transferable_range in transferable_ranges:
        fs.delete(transferable_range)


def _add(
    transferable_range: origin_models.TransferableRange,
    packet: protocol.OnTheWirePacket,
) -> None:
    """
    Add given TransferableRange to the given packet, mark it as TRANSFERRED
    and delete its associated data from filesystem.

    Args:
        transferable_range: django model for the TransferableRange to add
        packet: Pydantic protocol packet to add TransferableRange to

    """
    protocol_transferable = _build_protocol_transferable(transferable_range)

    try:
        protocol_transferable_range = protocol.TransferableRange(
            transferable=protocol_transferable,
            is_last=transferable_range.is_last,
            byte_offset=transferable_range.byte_offset,
            data=_get_transferable_range_data(transferable_range),
        )
    except exceptions.FileNotFoundError:
        transferable_range.mark_as_error()
        logger.error(
            {
                LOG_KEY: "data_file_not_found",
                "transferable_range_id": str(transferable_range.id),
                "transferable_id": str(transferable_range.outgoing_transferable.id),
            }
        )
        raise

    logger.info(
        {
            LOG_KEY: "adding_transferable_range",
            "transferable_id": str(transferable_range.outgoing_transferable.id),
            "transferable_range_id": str(transferable_range.id),
            "transferable_range_byte_offset": str(transferable_range.byte_offset),
        }
    )

    packet.transferable_ranges.append(protocol_transferable_range)

    transferable_range.mark_as_transferred()


def _cancel(
    transferable_range: origin_models.TransferableRange,
) -> None:
    """Mark the provided transferable_range as CANCELED and remove its data from the
    storage.
    """
    logger.info(
        {LOG_KEY: "cancelling_transferable", "transferable_id": str(transferable_range.outgoing_transferable.id)}
    )

    transferable_range.mark_as_canceled()


def _process(
    transferable_range: origin_models.TransferableRange,
    packet: protocol.OnTheWirePacket,
) -> int:
    """Process a transferable range by either adding it to the packet or cancelling
    it."""
    if (
        transferable_range.erroneous_outgoing_transferable_id is not None  # type: ignore # noqa: E501
        or hasattr(transferable_range.outgoing_transferable, "revocation")
    ):
        _cancel(transferable_range)
        return 0

    _add(transferable_range, packet)

    return transferable_range.size


class TransferableRangeFiller(base.OnTheWirePacketFiller):
    """
    Abstract filler.

    Fills the given packet with TransferableRange's data and metadata
    by calling the `fill()` method
    """

    def _get_transferable_ranges_to_process(
        self,
    ) -> Iterator[origin_models.TransferableRange]:
        """
        TransferableRange iterator

        Yields:
            TransferableRanges queried from DB
        """
        raise NotImplementedError()

    def fill(self, packet: protocol.OnTheWirePacket) -> None:
        """Given an OnTheWirePacket, fill it with TransferableRanges up to
        TRANSFERABLE_RANGE_SIZE bytes if it has no existing TransferableRanges.

        Args:
            packet: packet to fill with TransferableRanges

        Raises:
            OTWPacketAlreadyHasTransferableRanges: when passed a packet which already
                has TransferableRanges.

        """
        if len(packet.transferable_ranges) > 0:
            raise OTWPacketAlreadyHasTransferableRanges

        packet_size = 0

        to_delete = []

        for transferable_range in self._get_transferable_ranges_to_process():
            try:
                packet_size += _process(transferable_range, packet)
                to_delete.append(transferable_range)
            except exceptions.FileNotFoundError:
                pass

            if packet_size >= settings.TRANSFERABLE_RANGE_SIZE:
                break

        _delete_objects_from_fs(to_delete)


class UserRotatingTransferableRangeFiller(TransferableRangeFiller):
    """
    Fill the given packet with TransferableRange's data and metadata
    by calling the `fill()` method
    """

    def __init__(self) -> None:
        self._user_selector = user_selector.WeightedRoundRobinUserSelector()
        super().__init__()

    def _get_transferable_ranges_to_process(
        self,
    ) -> Iterator[origin_models.TransferableRange]:
        """
        TransferableRange iterator using the _user_selector

        Yields:
            TransferableRanges queried from DB
        """
        self._user_selector.start_round()

        while user := self._user_selector.get_next_user():
            yield from _fetch_next_transferable_ranges_for_user(user)


class FIFOTransferableRangeFiller(TransferableRangeFiller):
    """
    Fill the given packet with TransferableRange's data and metadata
    by calling the `fill()` method
    """

    def _get_transferable_ranges_to_process(
        self,
    ) -> Iterator[origin_models.TransferableRange]:
        """
        TransferableRange iterator

        Yields:
            TransferableRanges queried from DB
        """
        return iter(_fetch_pending_transferable_ranges())


__all__ = (
    "TransferableRangeFiller",
    "UserRotatingTransferableRangeFiller",
    "FIFOTransferableRangeFiller",
)
