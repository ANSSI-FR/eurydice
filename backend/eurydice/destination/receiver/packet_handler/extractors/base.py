import abc

import eurydice.common.protocol as protocol


class OnTheWirePacketExtractor(abc.ABC):
    """
    Abstract class for OnTheWirePacketExtractors.
    """

    @abc.abstractmethod
    def extract(self, packet: protocol.OnTheWirePacket) -> None:
        """
        Subclasses should implement this method to extract the required data
        from the given packet.

        Args:
            packet: packet to process.
        """
        raise NotImplementedError


__all__ = ("OnTheWirePacketExtractor",)
