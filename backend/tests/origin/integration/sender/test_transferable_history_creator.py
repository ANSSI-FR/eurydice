import datetime

import freezegun
import humanfriendly
import pytest
from django.conf import Settings
from django.utils import timezone

import tests.origin.integration.factory as factory
from eurydice.origin.core import enums
from eurydice.origin.core import models
from eurydice.origin.sender.transferable_history_creator import (
    TransferableHistoryCreator,
)


@pytest.fixture()
def pending_transferable():
    transferable = factory.OutgoingTransferableFactory(
        user_provided_meta={"Metadata-Foo": "Bar"},
    )
    factory.TransferableRangeFactory(
        transfer_state=enums.TransferableRangeTransferState.PENDING,
        outgoing_transferable=transferable,
    )
    return transferable


@pytest.fixture()
def ongoing_transferable():
    now = timezone.now() - datetime.timedelta(seconds=1)

    with freezegun.freeze_time(now):
        transferable = factory.OutgoingTransferableFactory(
            user_provided_meta={"Metadata-Foo": "Bar"},
        )
        factory.TransferableRangeFactory(
            transfer_state=enums.TransferableRangeTransferState.TRANSFERRED,
            outgoing_transferable=transferable,
            finished_at=now + datetime.timedelta(seconds=1),
        )
        factory.TransferableRangeFactory(
            transfer_state=enums.TransferableRangeTransferState.PENDING,
            outgoing_transferable=transferable,
            finished_at=None,
        )
    return transferable


@pytest.fixture()
def transferred_transferable():
    now = timezone.now() - datetime.timedelta(seconds=2)

    with freezegun.freeze_time(now):
        finish_date = now + datetime.timedelta(seconds=2)
        transferable = factory.OutgoingTransferableFactory(
            user_provided_meta={"Metadata-Foo": "Bar"},
            _submission_succeeded=True,
            _submission_succeeded_at=finish_date,
        )

        factory.TransferableRangeFactory(
            transfer_state=enums.TransferableRangeTransferState.TRANSFERRED,
            outgoing_transferable=transferable,
            finished_at=finish_date,
        )
    return transferable


@pytest.fixture()
def errored_transferable():
    now = timezone.now() - datetime.timedelta(seconds=2)

    with freezegun.freeze_time(now):
        transferable = factory.OutgoingTransferableFactory(
            user_provided_meta={"Metadata-Foo": "Bar"},
        )

        factory.TransferableRangeFactory(
            transfer_state=enums.TransferableRangeTransferState.ERROR,
            outgoing_transferable=transferable,
        )
    return transferable


def test_get_next_history_too_soon_returns_none(settings: Settings):
    settings.TRANSFERABLE_HISTORY_SEND_EVERY = humanfriendly.parse_timespan("1min")

    now = timezone.now()

    with freezegun.freeze_time(now):
        creator = TransferableHistoryCreator()
        creator._previous_history_generated_at = now - datetime.timedelta(seconds=1)
        assert creator.get_next_history() is None


@pytest.mark.django_db()
def test_get_next_history_no_returns_old_transferables(
    settings: Settings, transferred_transferable: models.OutgoingTransferable
):
    settings.TRANSFERABLE_HISTORY_DURATION = humanfriendly.parse_timespan("1h")

    now = transferred_transferable.submission_succeeded_at + datetime.timedelta(hours=2)

    with freezegun.freeze_time(now):
        creator = TransferableHistoryCreator()
        assert creator._previous_history_generated_at is None
        history = creator.get_next_history()

    assert history.entries == []
    assert creator._previous_history_generated_at == now


@pytest.mark.django_db()
def test_get_next_history_no_returns_non_final_state_transferables(
    settings: Settings,
    ongoing_transferable: models.OutgoingTransferable,
    pending_transferable: models.OutgoingTransferable,
):
    settings.TRANSFERABLE_HISTORY_DURATION_IN_HOURS = humanfriendly.parse_timespan("1h")

    now = ongoing_transferable.created_at + datetime.timedelta(minutes=15)

    with freezegun.freeze_time(now):
        creator = TransferableHistoryCreator()
        assert creator._previous_history_generated_at is None
        history = creator.get_next_history()

    assert history.entries == []
    assert creator._previous_history_generated_at == now


@pytest.mark.django_db()
def test_get_next_history_returns_final_state_transferables(
    settings: Settings,
    transferred_transferable: models.OutgoingTransferable,
    errored_transferable: models.OutgoingTransferable,
):
    settings.TRANSFERABLE_HISTORY_DURATION_IN_HOURS = humanfriendly.parse_timespan("1h")

    now = transferred_transferable.created_at + datetime.timedelta(minutes=15)

    with freezegun.freeze_time(now):
        creator = TransferableHistoryCreator()
        assert creator._previous_history_generated_at is None
        history = creator.get_next_history()

    history_entry_ids = [entry.transferable_id for entry in history.entries]

    expected_transferable_ids = [transferred_transferable.id, errored_transferable.id]

    assert sorted(history_entry_ids) == sorted(expected_transferable_ids)

    assert creator._previous_history_generated_at == now

    for entry in history.entries:
        assert entry.user_provided_meta == {"Metadata-Foo": "Bar"}
