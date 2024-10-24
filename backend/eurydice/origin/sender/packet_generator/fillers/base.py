import abc

import eurydice.common.protocol as protocol


class OnTheWirePacketFiller(abc.ABC):
    """
    Abstract class for OnTheWirePacketFillers.
    """

    @abc.abstractmethod
    def fill(self, packet: protocol.OnTheWirePacket) -> None:
        """
        Subclasses should implement this method to fill the given packet with their
        data.

        Args:
            packet: packet to fill.
        """
        raise NotImplementedError


__all__ = ("OnTheWirePacketFiller",)
