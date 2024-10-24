from eurydice.common import protocol
from eurydice.destination.receiver.packet_handler import extractors


class OnTheWirePacketHandler:
    """Allows for the processing of received OnTheWirePackets."""

    def __init__(self) -> None:
        self._extractors = (
            extractors.TransferableRangeExtractor(),
            extractors.TransferableRevocationExtractor(),
            extractors.OngoingHistoryExtractor(),
        )

    def handle(self, packet: protocol.OnTheWirePacket) -> None:
        """Handle a received OnTheWire packet by processing it using extractors.

        Args:
            packet: the received OnTheWirePacket to handle.

        """
        for extractor in self._extractors:
            extractor.extract(packet)


__all__ = ("OnTheWirePacketHandler",)
