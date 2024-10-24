import freezegun
import pytest
from django.db import connection
from django.utils import timezone
from faker import Faker

from eurydice.origin.core import enums
from eurydice.origin.core import models
from tests.origin.integration import factory


@pytest.mark.django_db()
def test_transferable_range_is_last_transferable_fully_submitted(faker: Faker):
    """
    Assert TransferableRange.is_last correctly identifies the last TransferableRange
    """

    transferable_size = faker.pyint(min_value=100)
    transferable_range_size = faker.pyint(min_value=1, max_value=transferable_size // 2)

    transferable = factory.OutgoingTransferableFactory(
        size=transferable_size,
        _submission_succeeded=True,
        _submission_succeeded_at=faker.date_time_this_decade(
            tzinfo=timezone.get_current_timezone()
        ),
    )

    second_to_last_range = factory.TransferableRangeFactory(
        byte_offset=transferable_size - transferable_range_size * 2,
        size=transferable_range_size,
        outgoing_transferable=transferable,
    )

    last_range = factory.TransferableRangeFactory(
        byte_offset=transferable_size - transferable_range_size,
        size=transferable_range_size,
        outgoing_transferable=transferable,
    )

    assert last_range.is_last is True
    assert second_to_last_range.is_last is False


@pytest.mark.django_db()
def test_transferable_range_is_last_shortcutting(faker: Faker):
    """
    Assert TransferableRange.is_last correctly shortcuts
    """

    transferable_size = faker.pyint(min_value=100)

    transferable = factory.OutgoingTransferableFactory(
        size=transferable_size,
        _submission_succeeded=True,
        _submission_succeeded_at=faker.date_time_this_decade(
            tzinfo=timezone.get_current_timezone()
        ),
    )

    only_range = factory.TransferableRangeFactory(
        byte_offset=0,
        size=transferable_size,
        outgoing_transferable=transferable,
    )

    num_queries = len(connection.queries)
    assert only_range.is_last is True
    assert num_queries == len(connection.queries)


@pytest.mark.django_db()
def test_transferable_range_is_last_transferable_not_fully_submitted():
    """
    Assert TransferableRange.is_last correctly returns False if associated
    Transferable is not finished uploading
    """

    transferable = factory.OutgoingTransferableFactory(
        submission_succeeded_at=None,
    )

    a_transferable_range = factory.TransferableRangeFactory(
        outgoing_transferable=transferable,
    )

    assert a_transferable_range.is_last is False


@pytest.mark.django_db()
def test_mark_as_transferred():
    transferable_range = factory.TransferableRangeFactory(
        transfer_state=enums.TransferableRangeTransferState.PENDING, finished_at=None
    )
    now = timezone.now()
    with freezegun.freeze_time(now):
        transferable_range.mark_as_transferred()

    queried_range = models.TransferableRange.objects.get(id=transferable_range.id)

    assert (
        queried_range.transfer_state == enums.TransferableRangeTransferState.TRANSFERRED
    )
    assert queried_range.finished_at == now


def test_mark_as_finished_no_save_success():
    transferable_range = factory.TransferableRangeFactory.build(
        transfer_state=enums.TransferableRangeTransferState.PENDING, finished_at=None
    )

    now = timezone.now()
    with freezegun.freeze_time(now):
        transferable_range._mark_as_finished(
            enums.TransferableRangeTransferState.TRANSFERRED, save=False
        )

    assert (
        transferable_range.transfer_state
        == enums.TransferableRangeTransferState.TRANSFERRED
    )
    assert transferable_range.finished_at == now
