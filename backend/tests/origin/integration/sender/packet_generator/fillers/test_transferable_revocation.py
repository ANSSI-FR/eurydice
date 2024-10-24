import pytest

import eurydice.common.protocol as protocol
import eurydice.origin.core.models as models
import eurydice.origin.sender.packet_generator.fillers as fillers
import tests.origin.integration.factory as factory
from eurydice.origin.core import enums


@pytest.mark.django_db()
def test_transferable_revocation_filler_fill_success():
    expected_transferable_revocation = factory.TransferableRevocationFactory(
        transfer_state=enums.TransferableRangeTransferState.PENDING
    )
    other_transferable_revocation = factory.TransferableRevocationFactory(
        transfer_state=enums.TransferableRangeTransferState.TRANSFERRED
    )

    filler = fillers.TransferableRevocationFiller()

    packet = protocol.OnTheWirePacket()

    filler.fill(packet)

    assert len(packet.transferable_revocations) == 1
    assert (
        packet.transferable_revocations[0].transferable_id
        == expected_transferable_revocation.outgoing_transferable.id
    )
    assert (
        models.TransferableRevocation.objects.get(
            id=expected_transferable_revocation.id
        ).transfer_state
        == enums.TransferableRangeTransferState.TRANSFERRED
    )
    assert (
        models.TransferableRevocation.objects.get(
            id=other_transferable_revocation.id
        ).transfer_state
        == enums.TransferableRangeTransferState.TRANSFERRED
    )
