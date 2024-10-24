from django.conf import settings

import eurydice.common.protocol as protocol
import eurydice.origin.sender.packet_generator.fillers as fillers
from eurydice.origin.core.models import Maintenance


class OnTheWirePacketGenerator:
    """
    Allows for the generation of filled OnTheWirePackets ready to be sent
    through the diode.
    """

    def __init__(self) -> None:
        range_filler_class = getattr(fillers, settings.SENDER_RANGE_FILLER_CLASS)
        self._fillers = (
            range_filler_class(),
            fillers.TransferableRevocationFiller(),
            fillers.OngoingHistoryFiller(),
        )

    def generate_next_packet(self) -> protocol.OnTheWirePacket:
        """
        Generate a new OnTheWirePacket and fill it with the fillers' content

        In maintenance mode, the returned packet is empty.

        Returns:
            the generated OnTheWirePacket
        """
        packet = protocol.OnTheWirePacket()  # type: ignore

        if not Maintenance.is_maintenance():
            for filler in self._fillers:
                filler.fill(packet)

        return packet


__all__ = ("OnTheWirePacketGenerator",)
