import datetime
from unittest import mock

import freezegun
import pytest
from django import conf
from django.utils import timezone
from faker import Faker

import eurydice.origin.cleaning.dbtrimmer.dbtrimmer as dbtrimmer_module
from eurydice.common.enums import OutgoingTransferableState
from eurydice.common.utils import signals
from eurydice.origin.cleaning.dbtrimmer.dbtrimmer import OriginDBTrimmer
from eurydice.origin.core import models
from tests.origin.integration import factory
from tests.utils import process_logs


@pytest.mark.django_db()
@pytest.mark.parametrize(
    (
        "transferable_states",
        "expected_deleted_transferables",
        "expected_deleted_ranges",
        "expected_deleted_revocations",
    ),
    [
        ([], 0, 0, 0),
        ([OutgoingTransferableState.PENDING], 0, 0, 0),
        ([OutgoingTransferableState.ONGOING], 0, 0, 0),
        ([OutgoingTransferableState.ERROR], 1, 0, 1),
        ([OutgoingTransferableState.CANCELED], 1, 0, 1),
        ([OutgoingTransferableState.SUCCESS], 1, 1, 0),
        (
            [
                OutgoingTransferableState.SUCCESS,
                OutgoingTransferableState.SUCCESS,
            ],
            2,
            2,
            0,
        ),
        (
            [
                OutgoingTransferableState.PENDING,
                OutgoingTransferableState.ONGOING,
                OutgoingTransferableState.ERROR,
                OutgoingTransferableState.CANCELED,
                OutgoingTransferableState.SUCCESS,
            ],
            3,
            1,
            2,
        ),
    ],
)
def test_dbtrimmer_by_transferable_states(
    faker: Faker,
    transferable_states: list[OutgoingTransferableState],
    expected_deleted_transferables: int,
    expected_deleted_ranges: int,
    expected_deleted_revocations: int,
    caplog: pytest.LogCaptureFixture,
    settings: conf.Settings,
):
    settings.DBTRIMMER_TRIM_TRANSFERABLES_AFTER = datetime.timedelta(seconds=1)

    now = faker.date_time_this_decade(tzinfo=timezone.get_current_timezone())

    for state in transferable_states:
        updated_at = now - settings.DBTRIMMER_TRIM_TRANSFERABLES_AFTER - datetime.timedelta(seconds=1)

        with freezegun.freeze_time(updated_at):
            factory.OutgoingTransferableFactory(
                _submission_succeeded=(state == OutgoingTransferableState.SUCCESS),
                _submission_succeeded_at=updated_at,
                make_transferable_ranges_for_state=state,
            )

    with freezegun.freeze_time(now):
        OriginDBTrimmer()._run()

    log_messages = process_logs(caplog.messages)

    if expected_deleted_ranges == 0 and expected_deleted_revocations == 0 and expected_deleted_transferables == 0:
        assert log_messages == [
            {"log_key": "db_trimmer_origin", "status": "running"},
            {"log_key": "db_trimmer_origin", "status": "done"},
        ]
    else:
        assert log_messages == [
            {"log_key": "db_trimmer_origin", "status": "running"},
            {
                "log_key": "db_trimmer_origin",
                "message": "DBTrimmer will remove OutgoingTransferables and all associated objects.",
                "outgoing_transferables_count": expected_deleted_transferables,
            },
            {
                "log_key": "db_trimmer_origin",
                "message": "DBTrimmer finished successfully",
                "deleted_transferables": expected_deleted_transferables,
                "deleted_ranges": expected_deleted_ranges,
                "deleted_revocations": expected_deleted_revocations,
            },
            {"log_key": "db_trimmer_origin", "status": "done"},
        ]

    assert not models.OutgoingTransferable.objects.filter(
        state__in=(
            OutgoingTransferableState.SUCCESS,
            OutgoingTransferableState.ERROR,
            OutgoingTransferableState.CANCELED,
        )
    ).exists()


@pytest.mark.django_db()
@pytest.mark.parametrize(
    ("time_delta", "expected_deletions", "expected_deleted_ranges"),
    [
        ([], 0, 0),
        ([datetime.timedelta(seconds=1)], 0, 0),
        ([datetime.timedelta(seconds=59)], 0, 0),
        ([datetime.timedelta(seconds=61)], 1, 0),
        (
            [
                datetime.timedelta(seconds=59),
                datetime.timedelta(seconds=61),
            ],
            1,
            0,
        ),
        (
            [
                datetime.timedelta(seconds=69),
                datetime.timedelta(seconds=71),
            ],
            2,
            0,
        ),
    ],
)
def test_dbtrimmer_by_transferable_finish_date(
    faker: Faker,
    time_delta: list[datetime.timedelta],
    expected_deletions: int,
    expected_deleted_ranges: int,
    caplog: pytest.LogCaptureFixture,
    settings: conf.Settings,
):
    settings.DBTRIMMER_TRIM_TRANSFERABLES_AFTER = datetime.timedelta(seconds=60)

    now = faker.date_time_this_decade(tzinfo=timezone.get_current_timezone())

    for delta in time_delta:
        submission_succeeded_at = now - delta
        with freezegun.freeze_time(submission_succeeded_at):
            factory.OutgoingTransferableFactory(
                _submission_succeeded=False,
                _submission_succeeded_at=submission_succeeded_at,
                make_transferable_ranges_for_state=OutgoingTransferableState.CANCELED,
            )

    with freezegun.freeze_time(now):
        OriginDBTrimmer()._run()

    log_messages = process_logs(caplog.messages)

    if expected_deletions == 0:
        assert log_messages == [
            {"log_key": "db_trimmer_origin", "status": "running"},
            {"log_key": "db_trimmer_origin", "status": "done"},
        ]
    else:
        assert log_messages == [
            {"log_key": "db_trimmer_origin", "status": "running"},
            {
                "log_key": "db_trimmer_origin",
                "message": "DBTrimmer will remove OutgoingTransferables and all associated objects.",
                "outgoing_transferables_count": expected_deletions,
            },
            {
                "log_key": "db_trimmer_origin",
                "message": "DBTrimmer finished successfully",
                "deleted_transferables": expected_deletions,
                "deleted_ranges": expected_deleted_ranges,
                "deleted_revocations": expected_deletions,
            },
            {"log_key": "db_trimmer_origin", "status": "done"},
        ]


@pytest.mark.django_db()
@mock.patch.object(signals.BooleanCondition, "__bool__")
@mock.patch("time.sleep")
def test_loop_success_no_transferable(
    time_sleep: mock.Mock,
    boolean_cond: mock.Mock,
):
    boolean_cond.side_effect = [True, True, False]
    dbtrimmer = OriginDBTrimmer()
    dbtrimmer._loop()
    assert time_sleep.call_count == 2


@mock.patch("eurydice.origin.core.models.OutgoingTransferable.objects.filter")
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
    filter_mock().delete.return_value = (None, {"": 0})

    OriginDBTrimmer()._run()

    log_messages = process_logs(caplog.messages)

    assert log_messages == [
        {"log_key": "db_trimmer_origin", "status": "running"},
        {
            "log_key": "db_trimmer_origin",
            "message": "DBTrimmer will remove OutgoingTransferables and all associated objects.",
            "outgoing_transferables_count": 1,
        },
        {
            "log_key": "db_trimmer_origin",
            "message": "DBTrimmer finished successfully",
            "deleted_transferables": 0,
            "deleted_ranges": 0,
            "deleted_revocations": 0,
        },
        {
            "log_key": "db_trimmer_origin",
            "message": "DBTrimmer deletion mismatch",
            "deleted_transferables": 0,
            "expected_deleted_transferables": 1,
        },
        {"log_key": "db_trimmer_origin", "status": "done"},
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
        OutgoingTransferableState.SUCCESS,
        OutgoingTransferableState.SUCCESS,
    ]:
        updated_at = now - settings.DBTRIMMER_TRIM_TRANSFERABLES_AFTER - datetime.timedelta(seconds=1)

        with freezegun.freeze_time(updated_at):
            factory.OutgoingTransferableFactory(
                _submission_succeeded=(state == OutgoingTransferableState.SUCCESS),
                _submission_succeeded_at=updated_at,
                make_transferable_ranges_for_state=state,
            )

    with freezegun.freeze_time(now):
        OriginDBTrimmer()._run()

    log_messages = process_logs(caplog.messages)

    assert log_messages == [
        {"log_key": "db_trimmer_origin", "status": "running"},
        {
            "log_key": "db_trimmer_origin",
            "message": "DBTrimmer will remove OutgoingTransferables and all associated objects.",
            "outgoing_transferables_count": 1,
        },
        {
            "log_key": "db_trimmer_origin",
            "message": "DBTrimmer finished successfully",
            "deleted_transferables": 1,
            "deleted_ranges": 1,
            "deleted_revocations": 0,
        },
        {
            "log_key": "db_trimmer_origin",
            "message": "DBTrimmer will remove OutgoingTransferables and all associated objects.",
            "outgoing_transferables_count": 1,
        },
        {
            "log_key": "db_trimmer_origin",
            "message": "DBTrimmer finished successfully",
            "deleted_transferables": 1,
            "deleted_ranges": 1,
            "deleted_revocations": 0,
        },
        {"log_key": "db_trimmer_origin", "status": "done"},
    ]

    assert not models.OutgoingTransferable.objects.filter(
        state__in=(
            OutgoingTransferableState.SUCCESS,
            OutgoingTransferableState.ERROR,
            OutgoingTransferableState.CANCELED,
        )
    ).exists()

    dbtrimmer_module.BULK_DELETION_SIZE = old_value
