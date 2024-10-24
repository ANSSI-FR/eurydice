import datetime

import freezegun
import pytest
from django.utils import timezone
from faker import Faker

from eurydice.origin.core import enums
from eurydice.origin.core import models
from tests.origin.integration import factory


@pytest.mark.django_db()
def test_list_pending_only_returns_pending_revocations():
    """
    Assert `list_pending` only returns `PENDING` revocations
    """

    for state in enums.TransferableRangeTransferState:
        if state != enums.TransferableRangeTransferState.PENDING:
            factory.TransferableRevocationFactory(transfer_state=state)

    assert not models.TransferableRevocation.objects.list_pending().exists()


@pytest.mark.django_db()
def test_list_pending_orders_by_creation_date(faker: Faker):
    """
    Assert that revocations are correctly ordered by date
    """

    a_date = faker.date_time_this_decade(tzinfo=timezone.get_current_timezone())

    with freezegun.freeze_time(a_date):
        expected_second_revocation = factory.TransferableRevocationFactory(
            transfer_state=enums.TransferableRangeTransferState.PENDING,
        )

    with freezegun.freeze_time(a_date - datetime.timedelta(seconds=1)):
        expected_first_revocation = factory.TransferableRevocationFactory(
            transfer_state=enums.TransferableRangeTransferState.PENDING,
        )

    revocations = models.TransferableRevocation.objects.list_pending()

    assert revocations.first() == expected_first_revocation
    assert revocations.last() == expected_second_revocation
