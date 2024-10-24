from unittest import mock

from eurydice.common import protocol
from eurydice.destination.receiver.packet_handler import packet_handler


class TestOnTheWirePacketHandler:
    @mock.patch(
        "eurydice.destination.receiver.packet_handler.packet_handler.extractors",
        autospec=True,
    )
    def test_constructor_success(self, mocked_extractors: mock.Mock):
        handler = packet_handler.OnTheWirePacketHandler()
        mocked_extractors.TransferableRangeExtractor.assert_called_once()
        mocked_extractors.TransferableRevocationExtractor.assert_called_once()
        mocked_extractors.OngoingHistoryExtractor.assert_called_once()

        assert len(handler._extractors) == 3

    @mock.patch(
        "eurydice.destination.receiver.packet_handler.packet_handler.extractors",
        autospec=True,
    )
    def test_handle_success(self, mocked_extractors: mock.Mock):
        handler = packet_handler.OnTheWirePacketHandler()
        packet = mock.Mock(autospec=protocol.OnTheWirePacket)
        handler.handle(packet)

        assert len(handler._extractors) == 3

        for extractor in handler._extractors:
            extractor.extract.assert_called_once_with(packet)
