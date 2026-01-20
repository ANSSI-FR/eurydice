import datetime
from unittest import mock

import freezegun
import pytest
from django import conf
from django.utils import timezone
from faker import Faker

import eurydice.destination.cleaning.dbtrimmer.dbtrimmer as dbtrimmer_module
from eurydice.common.utils import signals
from eurydice.destination.cleaning.dbtrimmer.dbtrimmer import DestinationDBTrimmer
from eurydice.destination.core import models
from tests.destination.integration import factory
from tests.utils import process_logs


@pytest.mark.django_db()
@pytest.mark.parametrize(
    ("transferable_states", "expected_deletions"),
    [
        ([], 0),
        ([models.IncomingTransferableState.ONGOING], 0),
        ([models.IncomingTransferableState.SUCCESS], 0),
        ([models.IncomingTransferableState.ERROR], 1),
        ([models.IncomingTransferableState.REVOKED], 1),
        ([models.IncomingTransferableState.EXPIRED], 1),
        ([models.IncomingTransferableState.REMOVED], 1),
        (
            [
                models.IncomingTransferableState.EXPIRED,
                models.IncomingTransferableState.EXPIRED,
            ],
            2,
        ),
        (
            [
                models.IncomingTransferableState.ONGOING,
                models.IncomingTransferableState.SUCCESS,
                models.IncomingTransferableState.ERROR,
                models.IncomingTransferableState.REVOKED,
                models.IncomingTransferableState.EXPIRED,
                models.IncomingTransferableState.REMOVED,
            ],
            4,
        ),
    ],
)
def test_dbtrimmer_by_transferable_states(
    faker: Faker,
    transferable_states: list[models.IncomingTransferableState],
    expected_deletions: int,
    caplog: pytest.LogCaptureFixture,
    settings: conf.Settings,
):
    settings.DBTRIMMER_TRIM_TRANSFERABLES_AFTER = datetime.timedelta(seconds=1)

    now = faker.date_time_this_decade(tzinfo=timezone.get_current_timezone())

    for state in transferable_states:
        created_at = now - settings.DBTRIMMER_TRIM_TRANSFERABLES_AFTER - datetime.timedelta(seconds=1)

        if state in models.IncomingTransferableState.get_final_states():
            finished_at = created_at
        else:
            finished_at = None

        factory.IncomingTransferableFactory(
            state=state,
            created_at=created_at,
            finished_at=finished_at,
        )

    with freezegun.freeze_time(now):
        DestinationDBTrimmer()._run()

    log_messages = process_logs(caplog.messages)

    if expected_deletions == 0:
        assert log_messages == [
            {"log_key": "dbtrimmer_destination", "status": "running"},
            {"log_key": "dbtrimmer_destination", "status": "done"},
        ]
    else:
        assert log_messages == [
            {"log_key": "dbtrimmer_destination", "status": "running"},
            {"log_key": "dbtrimmer_destination", "status": "success", "delete_count": expected_deletions},
            {"log_key": "dbtrimmer_destination", "status": "done"},
        ]

    assert not models.IncomingTransferable.objects.filter(
        state__in=(
            models.IncomingTransferableState.ERROR,
            models.IncomingTransferableState.REVOKED,
            models.IncomingTransferableState.EXPIRED,
            models.IncomingTransferableState.REMOVED,
        )
    ).exists()


@pytest.mark.django_db()
@pytest.mark.parametrize(
    ("transferable_finished_at", "expected_deletions"),
    [
        ([], 0),
        ([datetime.timedelta(seconds=1)], 0),
        ([datetime.timedelta(seconds=59)], 0),
        ([datetime.timedelta(seconds=61)], 1),
    ],
)
def test_dbtrimmer_by_transferable_finish_date(
    faker: Faker,
    transferable_finished_at: list[datetime.timedelta],
    expected_deletions: int,
    caplog: pytest.LogCaptureFixture,
    settings: conf.Settings,
):
    settings.DBTRIMMER_TRIM_TRANSFERABLES_AFTER = datetime.timedelta(seconds=60)

    now = faker.date_time_this_decade(tzinfo=timezone.get_current_timezone())

    for delta_finished_at in transferable_finished_at:
        finished_at = now - delta_finished_at
        factory.IncomingTransferableFactory(
            state=models.IncomingTransferableState.EXPIRED,
            created_at=finished_at,
            finished_at=finished_at,
        )

    with freezegun.freeze_time(now):
        DestinationDBTrimmer()._run()

    log_messages = process_logs(caplog.messages)

    if expected_deletions == 0:
        assert log_messages == [
            {"log_key": "dbtrimmer_destination", "status": "running"},
            {"log_key": "dbtrimmer_destination", "status": "done"},
        ]
    else:
        assert log_messages == [
            {"log_key": "dbtrimmer_destination", "status": "running"},
            {"log_key": "dbtrimmer_destination", "status": "success", "delete_count": expected_deletions},
            {"log_key": "dbtrimmer_destination", "status": "done"},
        ]


@pytest.mark.django_db()
@mock.patch.object(signals.BooleanCondition, "__bool__")
@mock.patch("time.sleep")
def test_loop_success_no_transferable(
    time_sleep: mock.Mock,
    boolean_cond: mock.Mock,
):
    boolean_cond.side_effect = [True, True, False]
    dbtrimmer = DestinationDBTrimmer()
    dbtrimmer._loop()
    assert time_sleep.call_count == 2


@mock.patch("eurydice.destination.core.models.IncomingTransferable.objects.filter")
@pytest.mark.django_db()
def test_deletion_count_mismatch_is_logged(
    filter_mock: mock.Mock,
    caplog: pytest.LogCaptureFixture,
):
    sliced_qs = mock.Mock()
    sliced_qs.values_list.return_value = ["xxx"]
    qs = mock.MagicMock()
    qs.__getitem__.return_value = sliced_qs
    filter_mock.return_value = qs
    filter_mock().delete.return_value = (0, None)

    DestinationDBTrimmer()._run()

    log_messages = process_logs(caplog.messages)

    assert log_messages == [
        {"log_key": "dbtrimmer_destination", "status": "running"},
        {"log_key": "dbtrimmer_destination", "status": "error", "delete_count": 0, "expected_delete_count": 1},
        {"log_key": "dbtrimmer_destination", "status": "done"},
    ]


@pytest.mark.django_db()
def test_dbtrimmer_bulk_delete(
    faker: Faker,
    caplog: pytest.LogCaptureFixture,
    settings: conf.Settings,
):
    old_value = dbtrimmer_module.BULK_DELETION_SIZE
    dbtrimmer_module.BULK_DELETION_SIZE = 1
    settings.DBTRIMMER_TRIM_TRANSFERABLES_AFTER = datetime.timedelta(seconds=1)

    now = faker.date_time_this_decade(tzinfo=timezone.get_current_timezone())

    for state in [
        models.IncomingTransferableState.EXPIRED,
        models.IncomingTransferableState.EXPIRED,
    ]:
        finished_at = now - settings.DBTRIMMER_TRIM_TRANSFERABLES_AFTER - datetime.timedelta(seconds=1)

        with freezegun.freeze_time(finished_at):
            factory.IncomingTransferableFactory(
                state=state,
                created_at=finished_at,
                finished_at=finished_at,
            )

    with freezegun.freeze_time(now):
        DestinationDBTrimmer()._run()

    log_messages = process_logs(caplog.messages)

    assert log_messages == [
        {"log_key": "dbtrimmer_destination", "status": "running"},
        {"log_key": "dbtrimmer_destination", "status": "success", "delete_count": 1},
        {"log_key": "dbtrimmer_destination", "status": "success", "delete_count": 1},
        {"log_key": "dbtrimmer_destination", "status": "done"},
    ]

    assert not models.IncomingTransferable.objects.filter(
        state__in=(
            models.IncomingTransferableState.ERROR,
            models.IncomingTransferableState.REVOKED,
            models.IncomingTransferableState.EXPIRED,
            models.IncomingTransferableState.REMOVED,
        )
    ).exists()

    dbtrimmer_module.BULK_DELETION_SIZE = old_value
