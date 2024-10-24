from typing import List

from eurydice.common import protocol
from eurydice.origin.core import enums
from eurydice.origin.core import models
from eurydice.origin.sender.packet_generator.fillers import base


def _create_packet_revocations() -> List[protocol.TransferableRevocation]:
    """Query the database and return PENDING TransferableRevocations as
    pydantic models, finally update the transfer_state for the queried
    TransferableRevocation.

    Returns:
        PENDING TransferableRevocations

    """
    revocations = []
    queried_revocations = models.TransferableRevocation.objects.select_related(  # type: ignore  # noqa: E501
        "outgoing_transferable__user_profile", "outgoing_transferable"
    ).list_pending()

    for revocation in queried_revocations:
        revocations.append(
            protocol.TransferableRevocation(
                transferable_id=revocation.outgoing_transferable.id,
                user_profile_id=revocation.outgoing_transferable.user_profile.id,
                transferable_name=revocation.outgoing_transferable.name,
                transferable_sha1=(
                    None
                    if not revocation.outgoing_transferable.sha1
                    else bytes(revocation.outgoing_transferable.sha1)
                ),
                reason=revocation.reason,
            )
        )

    queried_revocations.update(
        transfer_state=enums.TransferableRangeTransferState.TRANSFERRED
    )
    return revocations


class TransferableRevocationFiller(base.OnTheWirePacketFiller):
    """PacketFiller used to fill packet with TransferableRevocations"""

    def fill(self, packet: protocol.OnTheWirePacket) -> None:
        """Fill the given packet with PENDING TransferableRevocations.

        Args:
            packet: the packet to fill.

        """
        packet.transferable_revocations = _create_packet_revocations()


__all__ = ("TransferableRevocationFiller",)
