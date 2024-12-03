import datetime
import hashlib
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import freezegun
import pytest
from django.db.models.expressions import Value
from django.utils import timezone
from faker import Faker

from eurydice.common import enums
from eurydice.origin.core import enums as origin_enums
from eurydice.origin.core import models
from eurydice.origin.core.models import (
    outgoing_transferable as outgoing_transferable_model,
)
from tests.origin.integration import factory


@pytest.mark.django_db()
@pytest.mark.parametrize(
    (
        "submission_succeeded",
        "revocation_reason",
        "transferable_ranges_states",
        "expected_state",
    ),
    [
        # Test when Transferable has been canceled
        (
            False,
            enums.TransferableRevocationReason.USER_CANCELED,
            [],
            enums.OutgoingTransferableState.CANCELED,
        ),
        # Test when Transferable has been revoked for another reason
        (
            False,
            enums.TransferableRevocationReason.UPLOAD_SIZE_MISMATCH,
            [],
            enums.OutgoingTransferableState.ERROR,
        ),
        # Test when Transferable has been revoked for another reason
        (
            False,
            enums.TransferableRevocationReason.OBJECT_STORAGE_FULL,
            [],
            enums.OutgoingTransferableState.ERROR,
        ),
        # Test when Transferable has been revoked for another reason
        (
            False,
            enums.TransferableRevocationReason.UNEXPECTED_EXCEPTION,
            [],
            enums.OutgoingTransferableState.ERROR,
        ),
        # Test when Transferable submission in ongoing
        # but one TransferableRange has failed
        (
            False,
            None,
            [
                origin_enums.TransferableRangeTransferState.ERROR,
                origin_enums.TransferableRangeTransferState.TRANSFERRED,
            ],
            enums.OutgoingTransferableState.ERROR,
        ),
        # test when submission is finished and all TransferableRanges
        # have been transferred
        (
            True,
            None,
            [
                origin_enums.TransferableRangeTransferState.TRANSFERRED,
                origin_enums.TransferableRangeTransferState.TRANSFERRED,
            ],
            enums.OutgoingTransferableState.SUCCESS,
        ),
        # test when the submission is ongoing but not TransferableRange
        # has yet been created
        (
            False,
            None,
            [],
            enums.OutgoingTransferableState.PENDING,
        ),
        # test when submission is ongoing but TransferableRanges have not
        # yet been transferred
        (
            False,
            None,
            [
                origin_enums.TransferableRangeTransferState.PENDING,
                origin_enums.TransferableRangeTransferState.PENDING,
            ],
            enums.OutgoingTransferableState.PENDING,
        ),
        # test when submission is ongoing, one TransferableRange has been transferred
        # and another is still pending
        (
            False,
            None,
            [
                origin_enums.TransferableRangeTransferState.TRANSFERRED,
                origin_enums.TransferableRangeTransferState.PENDING,
            ],
            enums.OutgoingTransferableState.ONGOING,
        ),
        # test when submission is done but some TransferableRanges have not
        # yet been transferred
        (
            True,
            None,
            [
                origin_enums.TransferableRangeTransferState.TRANSFERRED,
                origin_enums.TransferableRangeTransferState.PENDING,
            ],
            enums.OutgoingTransferableState.ONGOING,
        ),
    ],
)
def test_outgoing_transferable_state(
    submission_succeeded: bool,
    revocation_reason: enums.TransferableRevocationReason,
    transferable_ranges_states: origin_enums.TransferableRangeTransferState,
    expected_state: enums.OutgoingTransferableState,
    faker: Faker,
):
    if submission_succeeded:
        submission_succeeded_at = faker.date_time_this_decade(
            tzinfo=timezone.get_current_timezone()
        )
    else:
        submission_succeeded_at = None

    outgoing_transferable = factory.OutgoingTransferableFactory(
        _submission_succeeded=submission_succeeded,
        _submission_succeeded_at=submission_succeeded_at,
    )

    if revocation_reason is not None:
        factory.TransferableRevocationFactory(
            reason=revocation_reason, outgoing_transferable=outgoing_transferable
        )

    for transferable_ranges_state in transferable_ranges_states:
        factory.TransferableRangeFactory(
            transfer_state=transferable_ranges_state,
            outgoing_transferable=outgoing_transferable,
        )

    queried_outgoing_transferable = models.OutgoingTransferable.objects.get(
        id=outgoing_transferable.id
    )

    assert queried_outgoing_transferable.state == expected_state


@pytest.mark.django_db()
@pytest.mark.parametrize(
    (
        "size_is_already_known",
        "transferable_ranges_states",
        "expected_progress",
    ),
    [
        # test when the submission is ongoing but no TransferableRange
        # has yet been created
        (
            False,
            [],
            None,
        ),
        # test when submission is ongoing but TransferableRanges have not
        # yet been transferred
        (
            False,
            [
                origin_enums.TransferableRangeTransferState.PENDING,
                origin_enums.TransferableRangeTransferState.PENDING,
            ],
            None,
        ),
        # test when submission is ongoing, one TransferableRange has been transferred
        # and another is still pending
        (
            False,
            [
                origin_enums.TransferableRangeTransferState.TRANSFERRED,
                origin_enums.TransferableRangeTransferState.PENDING,
            ],
            None,
        ),
        # test when submission is done but TransferableRanges have not
        # yet been transferred
        (
            True,
            [
                origin_enums.TransferableRangeTransferState.PENDING,
                origin_enums.TransferableRangeTransferState.PENDING,
            ],
            0,
        ),
        # test when submission is done but some TransferableRanges have not
        # yet been transferred
        (
            True,
            [
                origin_enums.TransferableRangeTransferState.TRANSFERRED,
                origin_enums.TransferableRangeTransferState.PENDING,
            ],
            50,
        ),
        # test when submission is done but some TransferableRanges have not
        # yet been transferred
        (
            True,
            [
                origin_enums.TransferableRangeTransferState.TRANSFERRED,
                origin_enums.TransferableRangeTransferState.TRANSFERRED,
                origin_enums.TransferableRangeTransferState.PENDING,
            ],
            66,
        ),
        # test when submission is finished and all TransferableRanges
        # have been transferred
        (
            True,
            [
                origin_enums.TransferableRangeTransferState.TRANSFERRED,
                origin_enums.TransferableRangeTransferState.TRANSFERRED,
            ],
            100,
        ),
        # Test when Transferable submission is done
        # but one TransferableRange has failed
        (
            True,
            [
                origin_enums.TransferableRangeTransferState.ERROR,
                origin_enums.TransferableRangeTransferState.TRANSFERRED,
            ],
            50,
        ),
    ],
)
def test_outgoing_transferable_progress(
    size_is_already_known: bool,
    transferable_ranges_states: origin_enums.TransferableRangeTransferState,
    expected_progress: int,
):
    transferable_range_length = 256

    outgoing_transferable = factory.OutgoingTransferableFactory(
        size=(
            transferable_range_length * len(transferable_ranges_states)
            if size_is_already_known
            else None
        ),
        _submission_succeeded=False,
    )

    for transferable_ranges_state in transferable_ranges_states:
        factory.TransferableRangeFactory(
            transfer_state=transferable_ranges_state,
            outgoing_transferable=outgoing_transferable,
            size=transferable_range_length,
        )

    queried_outgoing_transferable = models.OutgoingTransferable.objects.get(
        id=outgoing_transferable.id
    )

    assert queried_outgoing_transferable.progress == expected_progress


@pytest.mark.django_db()
@pytest.mark.parametrize(
    (
        "transferable_range_state",
        "expected_progress",
    ),
    [
        (origin_enums.TransferableRangeTransferState.PENDING, 0),
        (origin_enums.TransferableRangeTransferState.TRANSFERRED, 100),
    ],
)
def test_outgoing_transferable_progress_empty_file(
    transferable_range_state: origin_enums.TransferableRangeTransferState,
    expected_progress: int,
):
    outgoing_transferable = factory.OutgoingTransferableFactory(size=0)

    factory.TransferableRangeFactory(
        transfer_state=transferable_range_state,
        outgoing_transferable=outgoing_transferable,
        size=0,
    )

    queried_outgoing_transferable = models.OutgoingTransferable.objects.get(
        id=outgoing_transferable.id
    )

    assert queried_outgoing_transferable.progress == expected_progress


@pytest.mark.django_db()
@pytest.mark.parametrize(
    (
        "transferable_ranges_params",
        "outgoing_transferable_params",
        "expected_finished_at",
    ),
    [
        # test without any transferable ranges
        (
            [],
            {
                "size": 1,
                "submission_succeeded_at": None,
            },
            None,
        ),
        # test with null sized Transferable
        (
            [],
            {
                "size": 0,
                "submission_succeeded_at": None,
            },
            None,
        ),
        # test with null sized Transferable, sent
        (
            [
                {
                    "byte_offset": 0,
                    "size": 0,
                    "transfer_state": (
                        origin_enums.TransferableRangeTransferState.TRANSFERRED
                    ),
                    "finished_at": datetime.datetime(
                        2021, 1, 1, tzinfo=timezone.get_current_timezone()
                    ),
                }
            ],
            {
                "size": 0,
                "submission_succeeded_at": datetime.datetime(
                    2021, 1, 1, tzinfo=timezone.get_current_timezone()
                ),
            },
            datetime.datetime(2021, 1, 1, tzinfo=timezone.get_current_timezone()),
        ),
        # test with one Transferable Range but not all of them
        (
            [
                {
                    "byte_offset": 0,
                    "size": 1,
                    "transfer_state": (
                        origin_enums.TransferableRangeTransferState.TRANSFERRED
                    ),
                    "finished_at": datetime.datetime(
                        2021, 1, 1, tzinfo=timezone.get_current_timezone()
                    ),
                }
            ],
            {
                "size": 2,
                "submission_succeeded_at": None,
            },
            None,
        ),
        # test with one Transferable Range
        (
            [
                {
                    "byte_offset": 0,
                    "size": 1,
                    "transfer_state": (
                        origin_enums.TransferableRangeTransferState.TRANSFERRED
                    ),
                    "finished_at": datetime.datetime(
                        2021, 1, 1, tzinfo=timezone.get_current_timezone()
                    ),
                }
            ],
            {
                "size": 1,
                "submission_succeeded_at": datetime.datetime(
                    2021, 1, 1, tzinfo=timezone.get_current_timezone()
                ),
            },
            datetime.datetime(2021, 1, 1, tzinfo=timezone.get_current_timezone()),
        ),
        # test with two Transferable Ranges
        (
            [
                {
                    "byte_offset": 0,
                    "size": 1,
                    "transfer_state": (
                        origin_enums.TransferableRangeTransferState.TRANSFERRED
                    ),
                    "finished_at": datetime.datetime(
                        2021, 1, 1, tzinfo=timezone.get_current_timezone()
                    ),
                },
                {
                    "byte_offset": 1,
                    "size": 1,
                    "transfer_state": (
                        origin_enums.TransferableRangeTransferState.TRANSFERRED
                    ),
                    "finished_at": datetime.datetime(
                        2021, 2, 1, tzinfo=timezone.get_current_timezone()
                    ),
                },
            ],
            {
                "size": 2,
                "submission_succeeded_at": datetime.datetime(
                    2021, 1, 1, tzinfo=timezone.get_current_timezone()
                ),
            },
            datetime.datetime(2021, 2, 1, tzinfo=timezone.get_current_timezone()),
        ),
        # test with two Transferable Ranges, one not sent
        (
            [
                {
                    "byte_offset": 0,
                    "size": 1,
                    "transfer_state": (
                        origin_enums.TransferableRangeTransferState.TRANSFERRED
                    ),
                    "finished_at": datetime.datetime(
                        2021, 2, 1, tzinfo=timezone.get_current_timezone()
                    ),
                },
                {
                    "byte_offset": 1,
                    "size": 1,
                    "transfer_state": (
                        origin_enums.TransferableRangeTransferState.PENDING
                    ),
                    "finished_at": None,
                },
            ],
            {
                "size": 2,
                "submission_succeeded_at": datetime.datetime(
                    2021, 1, 1, tzinfo=timezone.get_current_timezone()
                ),
            },
            None,
        ),
    ],
)
def test_outgoing_transferable_range_finished_at(
    transferable_ranges_params: List[Dict[str, Any]],
    outgoing_transferable_params: Dict[str, Any],
    expected_finished_at: Optional[datetime.datetime],
):
    outgoing_transferable = factory.OutgoingTransferableFactory(
        **outgoing_transferable_params
    )

    # create transferable ranges in byte offset order
    for transferable_range_params in transferable_ranges_params:
        transferable_range_params["outgoing_transferable"] = outgoing_transferable
        with freezegun.freeze_time(transferable_range_params["finished_at"]):
            factory.TransferableRangeFactory(**transferable_range_params)

    queried_outgoing_transferable = models.OutgoingTransferable.objects.get(
        id=outgoing_transferable.id
    )

    assert queried_outgoing_transferable.finished_at == expected_finished_at


@pytest.mark.django_db()
@pytest.mark.parametrize(
    (
        "transferable_ranges_states",
        "expected_transferred_transferables_ranges_count",
    ),
    [
        # test with Transferred TransferableRanges
        (
            [
                origin_enums.TransferableRangeTransferState.TRANSFERRED,
                origin_enums.TransferableRangeTransferState.TRANSFERRED,
            ],
            2,
        ),
        # test with one pending TransferableRange
        (
            [
                origin_enums.TransferableRangeTransferState.TRANSFERRED,
                origin_enums.TransferableRangeTransferState.PENDING,
            ],
            1,
        ),
        # test without any TransferableRanges
        (
            [],
            0,
        ),
        # Test with TransferableRanges in all but the TRANSFERRED state
        (
            [
                origin_enums.TransferableRangeTransferState.PENDING,
                origin_enums.TransferableRangeTransferState.CANCELED,
                origin_enums.TransferableRangeTransferState.ERROR,
            ],
            0,
        ),
    ],
)
def test_auto_transferred_ranges_count_trigger(
    transferable_ranges_states: origin_enums.TransferableRangeTransferState,
    expected_transferred_transferables_ranges_count: int,
):
    outgoing_transferable = factory.OutgoingTransferableFactory()

    for transferable_ranges_state in transferable_ranges_states:
        factory.TransferableRangeFactory(
            transfer_state=transferable_ranges_state,
            outgoing_transferable=outgoing_transferable,
        )

    queried_outgoing_transferable = models.OutgoingTransferable.objects.get(
        id=outgoing_transferable.id
    )

    assert (
        queried_outgoing_transferable.auto_transferred_ranges_count
        == expected_transferred_transferables_ranges_count
    )


@pytest.mark.django_db()
def test_auto_state_update_trigger():
    outgoing_transferable = factory.OutgoingTransferableFactory(
        submission_succeeded_at=None,
        bytes_received=0,
        sha1=None,
        size=None,
    )

    old_value = outgoing_transferable.auto_state_updated_at

    assert old_value is not None

    new_value = old_value + datetime.timedelta(minutes=1)

    with freezegun.freeze_time(new_value):
        outgoing_transferable.sha1 = hashlib.sha1(b"0").digest()
        outgoing_transferable.size = 1
        outgoing_transferable.bytes_received = 1
        outgoing_transferable.submission_succeeded_at = new_value
        outgoing_transferable.save(
            update_fields=[
                "submission_succeeded_at",
                "bytes_received",
                "size",
                "sha1",
            ]
        )

    outgoing_transferable.refresh_from_db()
    assert outgoing_transferable.auto_state_updated_at == new_value


@pytest.mark.django_db()
def test_auto_state_update_trigger_not_altered_if_state_unchanged(faker: Faker):
    outgoing_transferable = factory.OutgoingTransferableFactory(
        submission_succeeded_at=faker.date_time_this_decade(
            tzinfo=timezone.get_current_timezone()
        ),
        bytes_received=1,
        sha1=hashlib.sha1(b"0").digest(),
        size=1,
    )

    old_value = outgoing_transferable.auto_state_updated_at

    with freezegun.freeze_time(
        outgoing_transferable.submission_succeeded_at + datetime.timedelta(hours=1)
    ):
        outgoing_transferable.name = "hey"
        outgoing_transferable.save(update_fields=["name"])

    outgoing_transferable.refresh_from_db()
    assert outgoing_transferable.auto_state_updated_at == old_value


@pytest.mark.django_db()
@pytest.mark.parametrize(
    (
        "transferable_ranges_params",
        "expected_bytes_transferred",
    ),
    [
        # test with Transferred TransferableRanges
        (
            [
                {
                    "transfer_state": (
                        origin_enums.TransferableRangeTransferState.TRANSFERRED
                    ),
                    "size": 1,
                },
                {
                    "transfer_state": (
                        origin_enums.TransferableRangeTransferState.TRANSFERRED
                    ),
                    "size": 1,
                },
            ],
            2,
        ),
        # test with one pending TransferableRange
        (
            [
                {
                    "transfer_state": (
                        origin_enums.TransferableRangeTransferState.TRANSFERRED
                    ),
                    "size": 1,
                },
                {
                    "transfer_state": (
                        origin_enums.TransferableRangeTransferState.PENDING
                    ),
                    "size": 1,
                },
            ],
            1,
        ),
        # test without any TransferableRanges
        (
            [],
            0,
        ),
        # Test with TransferableRanges in all but the TRANSFERRED state
        (
            [
                {
                    "transfer_state": (
                        origin_enums.TransferableRangeTransferState.PENDING
                    ),
                    "size": 1,
                },
                {
                    "transfer_state": (
                        origin_enums.TransferableRangeTransferState.CANCELED
                    ),
                    "size": 1,
                },
                {
                    "transfer_state": (
                        origin_enums.TransferableRangeTransferState.ERROR
                    ),
                    "size": 1,
                },
            ],
            0,
        ),
    ],
)
def test_bytes_transferred_annotation(
    transferable_ranges_params: List[dict],
    expected_bytes_transferred: int,
):
    outgoing_transferable = factory.OutgoingTransferableFactory()

    for transferable_range_params in transferable_ranges_params:
        transferable_range_params["outgoing_transferable"] = outgoing_transferable
        factory.TransferableRangeFactory(**transferable_range_params)

    queried_outgoing_transferable = models.OutgoingTransferable.objects.get(
        id=outgoing_transferable.id
    )

    assert (
        queried_outgoing_transferable.auto_bytes_transferred
        == expected_bytes_transferred
    )


@pytest.mark.django_db()
def test__build_transfer_duration_annotation_with_finished_at():
    """
    Test computing an OutgoingTransferable's `transfer_duration` when
    the transfer is finished
    """
    created_at = datetime.datetime(
        year=1998,
        month=2,
        day=4,
        tzinfo=timezone.get_current_timezone(),
    )
    finished_at = datetime.datetime(
        year=1998,
        month=2,
        day=5,
        tzinfo=timezone.get_current_timezone(),
    )
    expected_transfer_duration = datetime.timedelta(days=1).total_seconds()
    transferable_size = 2

    with freezegun.freeze_time(created_at):
        outgoing_transferable = factory.OutgoingTransferableFactory(
            size=transferable_size, submission_succeeded_at=finished_at
        )

        factory.TransferableRangeFactory(
            finished_at=finished_at,
            outgoing_transferable=outgoing_transferable,
            size=transferable_size,
            transfer_state=origin_enums.TransferableRangeTransferState.TRANSFERRED,
        )

    queried_outgoing_transferable = models.OutgoingTransferable.objects.annotate(
        transfer_duration=(
            outgoing_transferable_model._build_transfer_duration_annotation()
        )
    ).get(id=outgoing_transferable.id)

    assert queried_outgoing_transferable.transfer_duration == expected_transfer_duration


@pytest.mark.django_db()
def test__build_transfer_duration_annotation_no_finished_at(
    faker: Faker,
):
    """
    Test computing an OutgoingTransferable's `transfer_duration` when
    the transfer is not yet finished
    """
    created_at = faker.date_time_this_decade(tzinfo=timezone.get_current_timezone())
    finished_at = None
    transferable_size = 2
    current_datetime = timezone.now()

    with freezegun.freeze_time(created_at):
        outgoing_transferable = factory.OutgoingTransferableFactory(
            size=transferable_size, submission_succeeded_at=finished_at
        )

        factory.TransferableRangeFactory(
            finished_at=finished_at,
            outgoing_transferable=outgoing_transferable,
            size=transferable_size,
            transfer_state=origin_enums.TransferableRangeTransferState.PENDING,
        )

    with freezegun.freeze_time(current_datetime):
        queried_outgoing_transferable = models.OutgoingTransferable.objects.annotate(
            transfer_duration=(
                outgoing_transferable_model._build_transfer_duration_annotation()
            )
        ).get(id=outgoing_transferable.id)

    assert queried_outgoing_transferable.transfer_duration == int(
        round((current_datetime - created_at).total_seconds())
    )


@pytest.mark.django_db()
def test__build_speed_annotation_with_non_zero_transfer_duration():
    created_at = datetime.datetime(
        year=1998,
        month=2,
        day=4,
        tzinfo=timezone.get_current_timezone(),
    )
    finished_at = created_at + datetime.timedelta(seconds=1)
    transferable_size = 2
    expected_speed = 2

    with freezegun.freeze_time(created_at):
        outgoing_transferable = factory.OutgoingTransferableFactory(
            size=transferable_size, submission_succeeded_at=finished_at
        )

        factory.TransferableRangeFactory(
            finished_at=finished_at,
            outgoing_transferable=outgoing_transferable,
            size=transferable_size,
            transfer_state=origin_enums.TransferableRangeTransferState.TRANSFERRED,
        )

    queried_outgoing_transferable = models.OutgoingTransferable.objects.get(
        id=outgoing_transferable.id
    )

    assert queried_outgoing_transferable.speed == expected_speed


@pytest.mark.django_db()
def test__build_speed_annotation_with_zero_transfer_duration(
    faker: Faker,
):
    """
    Test when `speed` is 0 (transfer has just been created)
    """
    created_at = faker.date_time_this_decade(tzinfo=timezone.get_current_timezone())
    finished_at = None
    transferable_size = 2

    with freezegun.freeze_time(created_at):
        outgoing_transferable = factory.OutgoingTransferableFactory(
            size=transferable_size, submission_succeeded_at=finished_at
        )

        factory.TransferableRangeFactory(
            finished_at=finished_at,
            outgoing_transferable=outgoing_transferable,
            size=transferable_size,
            transfer_state=origin_enums.TransferableRangeTransferState.PENDING,
        )

        queried_outgoing_transferable = models.OutgoingTransferable.objects.get(
            id=outgoing_transferable.id
        )

    assert queried_outgoing_transferable.speed is None


@pytest.mark.django_db()
def test__build_estimated_finish_date_annotation_not_none(
    faker: Faker,
):
    outgoing_transferable = factory.OutgoingTransferableFactory(
        submission_succeeded_at=None, size=2
    )

    time_to_freeze = faker.date_time_this_decade(tzinfo=timezone.get_current_timezone())

    with freezegun.freeze_time(time_to_freeze):
        queried_outgoing_transferable = (
            models.OutgoingTransferable.objects.annotate(speed=Value(1))
            .annotate(
                estimated_finish_date=(
                    outgoing_transferable_model._build_estimated_finish_date_annotation()  # noqa: E501
                )
            )
            .get(id=outgoing_transferable.id)
        )

    assert (
        queried_outgoing_transferable.estimated_finish_date
        == time_to_freeze + datetime.timedelta(seconds=2)
    )


@pytest.mark.django_db()
def test__build_estimated_finish_date_annotation_speed_0():
    outgoing_transferable = factory.OutgoingTransferableFactory(
        submission_succeeded_at=None
    )

    queried_outgoing_transferable = (
        models.OutgoingTransferable.objects.annotate(speed=Value(0))
        .annotate(
            estimated_finish_date=(
                outgoing_transferable_model._build_estimated_finish_date_annotation()  # noqa: E501
            )
        )
        .get(id=outgoing_transferable.id)
    )

    assert queried_outgoing_transferable.estimated_finish_date is None


@pytest.mark.django_db()
def test__build_estimated_finish_date_annotation_submission_succeeded():
    outgoing_transferable = factory.OutgoingTransferableFactory(
        submission_succeeded_at=timezone.now()
    )

    queried_outgoing_transferable = models.OutgoingTransferable.objects.annotate(
        estimated_finish_date=(
            outgoing_transferable_model._build_estimated_finish_date_annotation()  # noqa: E501
        )
    ).get(id=outgoing_transferable.id)

    assert queried_outgoing_transferable.estimated_finish_date is None
