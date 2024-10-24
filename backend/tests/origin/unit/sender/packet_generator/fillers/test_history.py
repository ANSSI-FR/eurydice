from unittest import mock

from eurydice.common import protocol
from eurydice.origin.sender.packet_generator import fillers


def test_ongoing_history_filler_fill_success():
    filler = mock.Mock()

    expected_history = protocol.History(entries=[])
    filler._history_creator.get_next_history.return_value = expected_history
    packet = protocol.OnTheWirePacket()

    assert packet.history is None

    fillers.OngoingHistoryFiller.fill(filler, packet)

    assert packet.history is expected_history
