from unittest import mock

import pytest

import eurydice.common.protocol as protocol
from eurydice.origin.sender.packet_generator.fillers import (
    transferable_range as transferable_range_filler,
)


def test_transferable_range_filler__fill_already_exists_transferable_ranges_in_packet():  # noqa: E501
    """
    Assert `fill` method raises exception if passed a Packet which already contains
    TransferableRanges
    """
    packet = protocol.OnTheWirePacket()

    packet.transferable_ranges.append(1)

    mocked_filler = mock.Mock()

    with pytest.raises(transferable_range_filler.OTWPacketAlreadyHasTransferableRanges):
        transferable_range_filler.UserRotatingTransferableRangeFiller.fill(mocked_filler, packet)
