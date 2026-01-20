from datetime import datetime

import freezegun
import pytest

from eurydice.origin.backoffice.admin import OutgoingTransferableAdmin
from eurydice.origin.core.enums import TransferableRangeTransferState
from eurydice.origin.core.models.outgoing_transferable import OutgoingTransferable
from tests.origin.integration import factory


@pytest.mark.django_db()
@pytest.mark.parametrize(
    ("expected_finished_at", "expected_output"),
    [
        # Winter time
        (datetime.fromisoformat("2024-01-01 12:00:00+05:00"), "1 January 2024 08:00"),
        # Summer time
        (datetime.fromisoformat("2024-07-01 12:00:00+05:00"), "1 July 2024 09:00"),
    ],
)
def test_date_finished_at_should_be_right(
    expected_finished_at: datetime,
    expected_output: str,
) -> None:
    # generate fake OutgoingTransferable with
    # expected Success state and annotated field finished_at
    with freezegun.freeze_time(expected_finished_at):
        outgoing_transferable: OutgoingTransferable = factory.OutgoingTransferableFactory(
            size=0,
            submission_succeeded_at=expected_finished_at,
        )

        factory.TransferableRangeFactory(
            outgoing_transferable=outgoing_transferable,
            byte_offset=0,
            size=0,
            transfer_state=TransferableRangeTransferState.TRANSFERRED,
            finished_at=expected_finished_at,
        )

    queried_outgoing_transferable = OutgoingTransferable.objects.get(id=outgoing_transferable.id)

    assert queried_outgoing_transferable.finished_at == expected_finished_at

    result = OutgoingTransferableAdmin(OutgoingTransferable, admin_site="").finished_at(queried_outgoing_transferable)
    assert result == expected_output
