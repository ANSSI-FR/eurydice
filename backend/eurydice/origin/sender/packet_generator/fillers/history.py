from eurydice.common import protocol
from eurydice.origin.sender import transferable_history_creator as history_creator
from eurydice.origin.sender.packet_generator.fillers import base


class OngoingHistoryFiller(base.OnTheWirePacketFiller):
    """Fill the given packet with a TransferableHistory"""

    def __init__(self) -> None:  # pragma: no cover
        self._history_creator = history_creator.TransferableHistoryCreator()

    def fill(self, packet: protocol.OnTheWirePacket) -> None:
        """
        Fill the given packet with a TransferableHistory

        Args:
            packet: packet to fill
        """
        packet.history = self._history_creator.get_next_history()


__all__ = ("OngoingHistoryFiller",)
