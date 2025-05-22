import datetime
import hashlib
from pathlib import Path
from typing import List
from unittest import mock

import factory
import freezegun
import pytest
from django.conf import Settings
from django.utils import timezone
from faker import Faker

from eurydice.common import enums
from eurydice.common import exceptions
from eurydice.common import protocol
from eurydice.origin.core import enums as origin_enums
from eurydice.origin.core import models
from eurydice.origin.sender.packet_generator.fillers import (
    transferable_range as transferable_range_filler,
)
from eurydice.origin.sender.user_selector import WeightedRoundRobinUserSelector
from eurydice.origin.storage import fs
from tests.origin.integration import factory as origin_factory


@pytest.mark.django_db()
def test__build_protocol_transferable_expect_size_and_sha1():
    now = timezone.now() - datetime.timedelta(seconds=2)

    with freezegun.freeze_time(now):
        finish_date = now + datetime.timedelta(seconds=2)
        transferable = origin_factory.OutgoingTransferableFactory(
            submission_succeeded_at=finish_date,
        )

        origin_factory.TransferableRangeFactory(
            transfer_state=origin_enums.TransferableRangeTransferState.TRANSFERRED,
            outgoing_transferable=transferable,
            finished_at=finish_date,
        )

    # query in order to have state annotated
    queried_transferable = models.OutgoingTransferable.objects.prefetch_related(
        "transferable_ranges"
    ).get(id=transferable.id)
    protocol_transferable = transferable_range_filler._build_protocol_transferable(
        queried_transferable.transferable_ranges.select_related(
            "outgoing_transferable"
        ).last()
    )

    assert protocol_transferable.sha1 == bytes(transferable.sha1)


@pytest.mark.django_db()
def test__build_protocol_transferable(faker: Faker):
    transferable = origin_factory.OutgoingTransferableFactory(
        submission_succeeded_at=faker.date_time_this_decade(
            tzinfo=timezone.get_current_timezone()
        )
    )
    model = origin_factory.TransferableRangeFactory(outgoing_transferable=transferable)

    protocol_model = transferable_range_filler._build_protocol_transferable(model)

    assert model.outgoing_transferable.id == protocol_model.id
    assert model.outgoing_transferable.name == protocol_model.name
    assert model.outgoing_transferable.user_profile.id == protocol_model.user_profile_id
    assert (
        model.outgoing_transferable.user_provided_meta
        == protocol_model.user_provided_meta
    )
    assert bytes(model.outgoing_transferable.sha1) == protocol_model.sha1
    assert model.outgoing_transferable.size == protocol_model.size


@pytest.mark.django_db()
def test__build_protocol_transferable_no_sha1():
    model = origin_factory.TransferableRangeFactory(
        outgoing_transferable=origin_factory.OutgoingTransferableFactory(
            submission_succeeded_at=None, sha1=None
        )
    )

    protocol_model = transferable_range_filler._build_protocol_transferable(model)

    assert protocol_model.sha1 is None


@pytest.mark.django_db()
def test__delete_objects_from_fs__empty_list(faker: Faker) -> None:
    transferable_range_filler._delete_objects_from_fs([])


@pytest.mark.django_db()
def test__delete_objects_from_fs(faker: Faker, settings: Settings) -> None:
    data = faker.binary(length=10)
    folder_path = Path(settings.TRANSFERABLE_STORAGE_DIR)
    with (
        origin_factory.stored_transferable_ranges(
            data,
            2,
        ) as transferable_ranges,
        origin_factory.stored_transferable_range(data) as other_transferable_range,
    ):
        transferable_range_filler._delete_objects_from_fs(
            transferable_ranges + [other_transferable_range],
        )

        for transferable_range in transferable_ranges + [other_transferable_range]:
            file_path = folder_path / str(transferable_range.id)
            assert not file_path.exists()


@pytest.mark.django_db()
def test__get_transferable_range_data_success(faker: Faker):
    data = faker.binary(length=10)
    with origin_factory.stored_transferable_range(data) as transferable_range:
        fs_data = transferable_range_filler._get_transferable_range_data(
            transferable_range
        )
    assert hashlib.sha1(fs_data).digest() == hashlib.sha1(data).digest()


@pytest.mark.django_db()
def test__get_transferable_range_data_missing(faker: Faker):
    data = faker.binary(length=10)
    with origin_factory.stored_transferable_range(data) as transferable_range:
        fs.delete(transferable_range)
        with pytest.raises(exceptions.FileNotFoundError):
            transferable_range_filler._get_transferable_range_data(transferable_range)


@pytest.mark.django_db()
@pytest.mark.parametrize(
    "transfer_states",
    [
        [
            origin_enums.TransferableRangeTransferState.TRANSFERRED,
            origin_enums.TransferableRangeTransferState.PENDING,
            origin_enums.TransferableRangeTransferState.PENDING,
            origin_enums.TransferableRangeTransferState.TRANSFERRED,
            origin_enums.TransferableRangeTransferState.PENDING,
        ],
        [
            origin_enums.TransferableRangeTransferState.TRANSFERRED,
            origin_enums.TransferableRangeTransferState.ERROR,
            origin_enums.TransferableRangeTransferState.CANCELED,
        ],
    ],
)
def test__fetch_next_transferable_ranges(
    transfer_states: List[origin_enums.TransferableRangeTransferState],
):
    # add some noise
    origin_factory.TransferableRangeFactory.create_batch(
        len(origin_enums.TransferableRangeTransferState) * 3,
        transfer_state=factory.Iterator(
            origin_enums.TransferableRangeTransferState.values
        ),
    )

    # actual test
    current_user_profile = origin_factory.UserProfileFactory(priority=0)
    next_transferable_ranges = []

    for transfer_state in transfer_states:
        new_range = origin_factory.TransferableRangeFactory(
            outgoing_transferable__user_profile=current_user_profile,
            transfer_state=transfer_state,
        )

        if transfer_state == origin_enums.TransferableRangeTransferState.PENDING:
            next_transferable_ranges.append(new_range)

            # add an erroneous sibling, to also test the annotations
            origin_factory.TransferableRangeFactory(
                outgoing_transferable=new_range.outgoing_transferable,
                transfer_state=origin_enums.TransferableRangeTransferState.ERROR,
            )

    fetched = transferable_range_filler._fetch_next_transferable_ranges_for_user(
        current_user_profile.user
    )

    if next_transferable_ranges:
        assert len(fetched) == len(next_transferable_ranges)
        for elm in fetched:
            assert elm in next_transferable_ranges
            assert elm.erroneous_outgoing_transferable_id is not None
            assert (
                elm.erroneous_outgoing_transferable_id == elm.outgoing_transferable.id
            )
    else:
        assert len(fetched) == 0


@pytest.mark.django_db()
class TestTransferableRangeFiller:
    def test_fill_success(self, faker: Faker, settings: Settings):
        """
        Assert filler fills the packet with the correct transferable range
        Also assert that the TransferableRange's status was updated correctly.
        """
        filler = transferable_range_filler.UserRotatingTransferableRangeFiller()
        packet = protocol.OnTheWirePacket()
        folder_path = Path(settings.TRANSFERABLE_STORAGE_DIR)
        data = faker.binary(length=10)
        with origin_factory.stored_transferable_range(
            data, transfer_state=origin_enums.TransferableRangeTransferState.PENDING
        ) as transferable_range:
            a_date = timezone.now()
            with freezegun.freeze_time(a_date):
                filler.fill(packet=packet)

            transferable_range.refresh_from_db()
            file_path = folder_path / str(transferable_range.id)

            assert not file_path.exists()

        assert len(packet.transferable_ranges) == 1
        assert packet.transferable_ranges[0].data == data

        assert (
            transferable_range.transfer_state
            == origin_enums.TransferableRangeTransferState.TRANSFERRED
        )
        assert transferable_range.finished_at == a_date

    def test_fill_no_pending_transferable_range(self):
        """
        Asserts `fill` returns an empty list when there are no PENDING
        TransferableRanges
        """

        filler = transferable_range_filler.UserRotatingTransferableRangeFiller()

        packet = protocol.OnTheWirePacket()

        origin_factory.TransferableRangeFactory(
            transfer_state=origin_enums.TransferableRangeTransferState.TRANSFERRED
        )

        transferable_range_filler.UserRotatingTransferableRangeFiller.fill(
            filler, packet
        )

        assert packet.transferable_ranges == []

    def test_fill_no_next_user(self):
        """
        Asserts `fill` returns an empty list when there are no next users
        """

        filler = transferable_range_filler.UserRotatingTransferableRangeFiller()
        packet = protocol.OnTheWirePacket()

        transferable_range_filler.UserRotatingTransferableRangeFiller.fill(
            filler, packet
        )

        assert packet.transferable_ranges == []

    @mock.patch(
        "eurydice.origin.sender.packet_generator.fillers.transferable_range._delete_objects_from_fs"  # noqa: E501
    )
    def test_fill_cancel_revoked_transferable_ranges(
        self, mocked_delete_objects_from_fs: mock.Mock
    ):
        filler = transferable_range_filler.UserRotatingTransferableRangeFiller()
        packet = protocol.OnTheWirePacket()

        outgoing_transferable = origin_factory.OutgoingTransferableFactory()

        transferable_range = origin_factory.TransferableRangeFactory(
            transfer_state=origin_enums.TransferableRangeTransferState.PENDING,
            outgoing_transferable=outgoing_transferable,
        )

        origin_factory.TransferableRevocationFactory(
            reason=enums.TransferableRevocationReason.UPLOAD_SIZE_MISMATCH,
            outgoing_transferable=outgoing_transferable,
        )

        outgoing_transferable = models.OutgoingTransferable.objects.get(
            id=outgoing_transferable.id
        )
        assert outgoing_transferable.state == enums.OutgoingTransferableState.ERROR

        filler.fill(packet)

        transferable_range.refresh_from_db()
        assert (
            transferable_range.transfer_state
            == origin_enums.TransferableRangeTransferState.CANCELED
        )
        mocked_delete_objects_from_fs.assert_called_once()

        assert packet.transferable_ranges == []

    @mock.patch(
        "eurydice.origin.sender.packet_generator.fillers.transferable_range._get_transferable_range_data"  # noqa: E501
    )
    @mock.patch(
        "eurydice.origin.sender.packet_generator.fillers.transferable_range._delete_objects_from_fs"  # noqa: E501
    )
    def test_transferable_range_filler_fill_packet_size_too_large(
        self,
        patched_delete_objects_from_fs: mock.MagicMock,
        patched_next_tr_data: mock.MagicMock,
        settings: Settings,
    ):
        """
        Asserts `fill` stops adding transferable_ranges after the configured
        TRANSFERABLE_RANGE_SIZE is exceeded
        """

        # prepare mocked functions
        first_user_ranges = origin_factory.TransferableRangeFactory.create_batch(
            2,
            transfer_state=origin_enums.TransferableRangeTransferState.PENDING,
            outgoing_transferable__user_profile=origin_factory.UserProfileFactory(),
        )

        second_user_range = origin_factory.TransferableRangeFactory(
            transfer_state=origin_enums.TransferableRangeTransferState.PENDING
        )

        patched_next_tr_data.return_value = (
            b"It was a bright cold day in April, and the clocks were striking thirteen"
        )

        patched_delete_objects_from_fs.return_value = None

        # also mock the user selector
        mocked_user_selector = mock.create_autospec(WeightedRoundRobinUserSelector)
        mocked_user_selector.get_next_user.side_effect = [
            first_user_ranges[0].outgoing_transferable.user_profile.user,
            second_user_range.outgoing_transferable.user_profile.user,
            None,
            RuntimeError("get_next_user called too many times"),
        ]

        # actual test
        settings.TRANSFERABLE_RANGE_SIZE = 0

        filler = transferable_range_filler.UserRotatingTransferableRangeFiller()
        filler._user_selector = mocked_user_selector
        packet = protocol.OnTheWirePacket()
        transferable_range_filler.UserRotatingTransferableRangeFiller.fill(
            filler, packet
        )

        assert len(packet.transferable_ranges) == 1
        assert (
            packet.transferable_ranges[0].transferable.id
            == first_user_ranges[0].outgoing_transferable.id
        )
        patched_delete_objects_from_fs.assert_called_once()
        mocked_user_selector.get_next_user.assert_called_once()

    def test_fill_missing_file(self, faker: Faker):
        filler = transferable_range_filler.UserRotatingTransferableRangeFiller()
        packet = protocol.OnTheWirePacket()

        data = faker.binary(length=10)
        with origin_factory.stored_transferable_range(
            data, transfer_state=origin_enums.TransferableRangeTransferState.PENDING
        ) as transferable_range:
            fs.delete(transferable_range)
            a_date = timezone.now()
            with freezegun.freeze_time(a_date):
                filler.fill(packet=packet)

            transferable_range.refresh_from_db()

        assert len(packet.transferable_ranges) == 0

        assert (
            transferable_range.transfer_state
            == origin_enums.TransferableRangeTransferState.ERROR
        )

        assert transferable_range.finished_at == a_date


@pytest.mark.django_db()
class TestFIFOTransferableRangeFiller:
    def test_fill_success(self, faker: Faker, settings: Settings):
        """
        Assert filler fills the packet with the correct transferable range.
        Also assert that the TransferableRange's status was updated correctly.
        """
        filler = transferable_range_filler.FIFOTransferableRangeFiller()
        packet = protocol.OnTheWirePacket()
        folder_path = Path(settings.TRANSFERABLE_STORAGE_DIR)

        data = faker.binary(length=10)
        with origin_factory.stored_transferable_range(
            data, transfer_state=origin_enums.TransferableRangeTransferState.PENDING
        ) as transferable_range:
            a_date = timezone.now()
            with freezegun.freeze_time(a_date):
                filler.fill(packet=packet)

            transferable_range.refresh_from_db()
            file_path = folder_path / str(transferable_range.id)
            assert not file_path.exists()

        assert len(packet.transferable_ranges) == 1
        assert packet.transferable_ranges[0].data == data

        assert (
            transferable_range.transfer_state
            == origin_enums.TransferableRangeTransferState.TRANSFERRED
        )
        assert transferable_range.finished_at == a_date


@pytest.mark.django_db()
def test_fetch_next_transferable_ranges_for_user_only_returns_user_transferable_ranges(
    faker: Faker,
):
    """
    Assert _fetch_next_transferable_ranges_for_user only returns TransferableRanges
    for the given user.
    """

    user_profile = origin_factory.UserProfileFactory()
    another_user_profile = origin_factory.UserProfileFactory()

    a_date = faker.date_time_this_decade(tzinfo=timezone.get_current_timezone())

    with freezegun.freeze_time(a_date):
        expected_transferable_range = origin_factory.TransferableRangeFactory(
            outgoing_transferable=origin_factory.OutgoingTransferableFactory(
                user_profile=user_profile
            ),
            transfer_state=origin_enums.TransferableRangeTransferState.PENDING,
            finished_at=None,
        )

    with freezegun.freeze_time(a_date - datetime.timedelta(seconds=1)):
        origin_factory.TransferableRangeFactory(
            outgoing_transferable=origin_factory.OutgoingTransferableFactory(
                user_profile=another_user_profile
            ),
            transfer_state=origin_enums.TransferableRangeTransferState.PENDING,
            finished_at=None,
        )

    assert (
        transferable_range_filler._fetch_next_transferable_ranges_for_user(
            user_profile.user
        ).first()
        == expected_transferable_range
    )


@pytest.mark.django_db()
def test_fetch_next_transferable_ranges_for_user_returns_nothing():
    """
    Assert _fetch_next_transferable_ranges_for_user returns nothing when passed
    user_profile without any associated TransferableRanges
    """

    user_profile = origin_factory.UserProfileFactory()

    assert (
        transferable_range_filler._fetch_next_transferable_ranges_for_user(
            user_profile.user
        ).count()
        == 0
    )


@pytest.mark.django_db()
def test_fetch_next_transferable_ranges_for_user_returns_oldest_transferable_range(
    faker: Faker,
):
    """
    Assert _fetch_next_transferable_ranges_for_user returns the oldest of two
    TransferableRanges both belonging to the given user.
    """

    user_profile = origin_factory.UserProfileFactory()

    a_date = faker.date_time_this_decade(tzinfo=timezone.get_current_timezone())

    with freezegun.freeze_time(a_date):
        origin_factory.TransferableRangeFactory(
            outgoing_transferable=origin_factory.OutgoingTransferableFactory(
                user_profile=user_profile
            ),
            transfer_state=origin_enums.TransferableRangeTransferState.PENDING,
            finished_at=None,
        )

    with freezegun.freeze_time(a_date - datetime.timedelta(seconds=1)):
        expected_transferable_range = origin_factory.TransferableRangeFactory(
            outgoing_transferable=origin_factory.OutgoingTransferableFactory(
                user_profile=user_profile
            ),
            transfer_state=origin_enums.TransferableRangeTransferState.PENDING,
            finished_at=None,
        )

    assert (
        transferable_range_filler._fetch_next_transferable_ranges_for_user(
            user_profile.user
        ).first()
        == expected_transferable_range
    )


@pytest.mark.django_db()
def test_fetch_next_transferable_ranges_for_user_filters_finished_transferable_ranges(
    faker: Faker,
):
    """
    Assert _fetch_next_transferable_ranges_for_user filters out finished
    TransferableRanges
    """
    a_date = faker.date_time_this_decade(tzinfo=timezone.get_current_timezone())

    with freezegun.freeze_time(a_date - datetime.timedelta(seconds=2)):
        transferable_range = origin_factory.TransferableRangeFactory(
            transfer_state=origin_enums.TransferableRangeTransferState.TRANSFERRED,
            finished_at=a_date,
        )

    assert (
        transferable_range_filler._fetch_next_transferable_ranges_for_user(
            transferable_range.outgoing_transferable.user_profile.user
        ).count()
        == 0
    )


@pytest.mark.django_db()
def test_fetch_pending_transferable_ranges_returns_transferable_ranges_for_any_user(
    faker: Faker,
):
    """
    Assert _fetch_pending_transferable_ranges returns TransferableRanges for any user.
    """

    user_profile = origin_factory.UserProfileFactory()
    another_user_profile = origin_factory.UserProfileFactory()

    a_date = faker.date_time_this_decade(tzinfo=timezone.get_current_timezone())

    with freezegun.freeze_time(a_date):
        expected_transferable_range_user_1 = origin_factory.TransferableRangeFactory(
            outgoing_transferable=origin_factory.OutgoingTransferableFactory(
                user_profile=user_profile
            ),
            transfer_state=origin_enums.TransferableRangeTransferState.PENDING,
            finished_at=None,
        )

    with freezegun.freeze_time(a_date - datetime.timedelta(seconds=1)):
        expected_transferable_range_user_2 = origin_factory.TransferableRangeFactory(
            outgoing_transferable=origin_factory.OutgoingTransferableFactory(
                user_profile=another_user_profile
            ),
            transfer_state=origin_enums.TransferableRangeTransferState.PENDING,
            finished_at=None,
        )

    assert list(transferable_range_filler._fetch_pending_transferable_ranges()) == [
        expected_transferable_range_user_2,
        expected_transferable_range_user_1,
    ]


@pytest.mark.django_db()
def test_fetch_pending_transferable_ranges_returns_nothing():
    """
    Assert _fetch_pending_transferable_ranges returns nothing when passed
    there are no pending TransferableRanges
    """
    assert transferable_range_filler._fetch_pending_transferable_ranges().count() == 0


@pytest.mark.django_db()
def test_fetch_pending_transferable_ranges_returns_oldest_transferable_range(
    faker: Faker,
):
    """
    Assert _fetch_pending_transferable_ranges returns the oldest of two
    TransferableRanges.
    """

    user_profile = origin_factory.UserProfileFactory()

    a_date = faker.date_time_this_decade(tzinfo=timezone.get_current_timezone())

    with freezegun.freeze_time(a_date):
        origin_factory.TransferableRangeFactory(
            outgoing_transferable=origin_factory.OutgoingTransferableFactory(
                user_profile=user_profile
            ),
            transfer_state=origin_enums.TransferableRangeTransferState.PENDING,
            finished_at=None,
        )

    with freezegun.freeze_time(a_date - datetime.timedelta(seconds=1)):
        expected_transferable_range = origin_factory.TransferableRangeFactory(
            outgoing_transferable=origin_factory.OutgoingTransferableFactory(
                user_profile=user_profile
            ),
            transfer_state=origin_enums.TransferableRangeTransferState.PENDING,
            finished_at=None,
        )

    assert (
        transferable_range_filler._fetch_pending_transferable_ranges().first()
        == expected_transferable_range
    )


@pytest.mark.django_db()
def test_fetch_pending_transferable_ranges_filters_finished_transferable_ranges(
    faker: Faker,
):
    """
    Assert _fetch_pending_transferable_ranges filters out finished
    TransferableRanges
    """
    a_date = faker.date_time_this_decade(tzinfo=timezone.get_current_timezone())

    with freezegun.freeze_time(a_date - datetime.timedelta(seconds=2)):
        origin_factory.TransferableRangeFactory(
            transfer_state=origin_enums.TransferableRangeTransferState.TRANSFERRED,
            finished_at=a_date,
        )

    assert transferable_range_filler._fetch_pending_transferable_ranges().count() == 0
