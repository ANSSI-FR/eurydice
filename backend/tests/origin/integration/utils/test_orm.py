import factory
import pytest
from django.db.models import F
from django.db.models import Q

from eurydice.common.utils import orm
from eurydice.origin.core import enums
from eurydice.origin.core import models
from tests.origin.integration import factory as origin_factory


@pytest.mark.django_db()
def test_outgoing_transferable_state():
    # Create a pending transferable range for an erroneous outgoing transferable
    erroneous_outgoing_transferable = origin_factory.OutgoingTransferableFactory(
        _submission_succeeded=True,
    )

    origin_factory.TransferableRangeFactory.create_batch(
        3,
        transfer_state=factory.Iterator(
            (
                enums.TransferableRangeTransferState.TRANSFERRED,
                enums.TransferableRangeTransferState.ERROR,
                enums.TransferableRangeTransferState.PENDING,
            )
        ),
        outgoing_transferable=erroneous_outgoing_transferable,
    )

    # Create a basic pending transferable range
    pending_outgoing_transferable = origin_factory.OutgoingTransferableFactory(
        _submission_succeeded=True,
    )

    origin_factory.TransferableRangeFactory(
        transfer_state=enums.TransferableRangeTransferState.PENDING,
        outgoing_transferable=pending_outgoing_transferable,
    )

    # Black magic
    queryset = orm.make_queryset_with_subquery_join(
        models.TransferableRange.objects.only("id").filter(
            transfer_state=enums.TransferableRangeTransferState.PENDING
        ),
        models.TransferableRange.objects.values("outgoing_transferable_id").filter(
            transfer_state=enums.TransferableRangeTransferState.ERROR
        ),
        on=Q(outgoing_transferable_id=F("outgoing_transferable_id")),
        select={"erroneous_outgoing_transferable_id": "outgoing_transferable_id"},
    )

    # Checks
    assert len(queryset) == 2

    found_pending = False
    found_erroneous = False

    for transferable_range in queryset:
        if transferable_range.outgoing_transferable == pending_outgoing_transferable:
            found_pending = True
            assert transferable_range.erroneous_outgoing_transferable_id is None

        if transferable_range.outgoing_transferable == erroneous_outgoing_transferable:
            found_erroneous = True
            assert (
                transferable_range.erroneous_outgoing_transferable_id
                == erroneous_outgoing_transferable.id
            )

    assert found_erroneous
    assert found_pending
