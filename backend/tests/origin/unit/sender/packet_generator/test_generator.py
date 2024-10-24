from unittest import mock

import pytest

import eurydice.origin.sender.packet_generator.fillers as fillers
import eurydice.origin.sender.packet_generator.generator as generator


@pytest.mark.django_db()
@mock.patch.object(fillers.UserRotatingTransferableRangeFiller, "fill")
@mock.patch.object(fillers.TransferableRevocationFiller, "fill")
@mock.patch.object(fillers.OngoingHistoryFiller, "fill")
def test_generator_generate_next_packet(
    fill_transferable_ranges: fillers.UserRotatingTransferableRangeFiller,
    fill_revocations: fillers.TransferableRevocationFiller,
    fill_history: fillers.OngoingHistoryFiller,
):
    packet_generator = generator.OnTheWirePacketGenerator()
    fill_transferable_ranges.return_value = 1

    packet = packet_generator.generate_next_packet()

    fill_transferable_ranges.assert_called_once_with(packet)
    fill_revocations.assert_called_once_with(packet)
    fill_history.assert_called_once_with(packet)
