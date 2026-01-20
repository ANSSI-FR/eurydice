import functools
import hashlib
import logging
from unittest import mock

import pytest
from faker import Faker

import eurydice.destination.core.models as models
import eurydice.destination.receiver.packet_handler.extractors.transferable_range as transferable_range  # noqa: E501
import eurydice.destination.utils.rehash as rehash
import tests.common.integration.factory as protocol_factory
import tests.destination.integration.factory as factory
from eurydice.destination.core.models.incoming_transferable import (
    IncomingTransferableState,
)


@pytest.mark.django_db()
def test__get_or_create_transferable_new_user_profile_new_transferable():
    a_transferable_range = protocol_factory.TransferableRangeFactory()

    assert models.UserProfile.objects.count() == 0
    assert models.IncomingTransferable.objects.count() == 0

    transferable = transferable_range._get_or_create_transferable(a_transferable_range)

    assert models.UserProfile.objects.count() == 1

    assert models.IncomingTransferable.objects.count() == 1
    assert transferable.size == a_transferable_range.transferable.size
    assert transferable.sha1 is None


@pytest.mark.django_db()
def test__get_or_create_transferable_existing_user_profile_new_transferable():
    user_profile = factory.UserProfileFactory()
    a_transferable_range = protocol_factory.TransferableRangeFactory(
        transferable=protocol_factory.TransferableFactory(user_profile_id=user_profile.associated_user_profile_id)
    )

    assert models.UserProfile.objects.count() == 1

    transferable = transferable_range._get_or_create_transferable(a_transferable_range)

    assert models.UserProfile.objects.count() == 1
    assert transferable.user_profile == user_profile

    assert models.IncomingTransferable.objects.count() == 1
    assert transferable.size == a_transferable_range.transferable.size
    assert transferable.sha1 is None


@pytest.mark.django_db()
def test__get_or_create_transferable_existing_user_profile_existing_transferable():
    user_profile = factory.UserProfileFactory()
    expected_transferable = factory.IncomingTransferableFactory(
        state=models.IncomingTransferableState.ONGOING, user_profile=user_profile
    )

    a_transferable_range = protocol_factory.TransferableRangeFactory(
        transferable=protocol_factory.TransferableFactory(
            id=expected_transferable.id,
            user_profile_id=user_profile.associated_user_profile_id,
        ),
    )

    assert models.UserProfile.objects.count() == 1
    assert models.IncomingTransferable.objects.count() == 1

    transferable = transferable_range._get_or_create_transferable(a_transferable_range)

    assert models.UserProfile.objects.count() == 1
    assert models.IncomingTransferable.objects.count() == 1
    assert transferable.user_profile == user_profile

    assert transferable == expected_transferable


@pytest.mark.parametrize(
    ("transferable_bytes_received", "byte_offset", "expected_exception"),
    [
        (0, 1, transferable_range.MissedTransferableRangeError),
        (0, 0, None),
        (1, 1, None),
        (1, 2, transferable_range.MissedTransferableRangeError),
    ],
)
def test__assert_no_transferable_ranges_were_missed(
    transferable_bytes_received: int,
    byte_offset: int,
    expected_exception: bool,
    faker: Faker,
):
    mocked_transferable = mock.create_autospec(models.IncomingTransferable)
    mocked_transferable.bytes_received = transferable_bytes_received

    a_uuid = faker.uuid4()
    # mock.create_autospec does not seem to work for class attributes
    mocked_transferable_range = mock.Mock()
    mocked_transferable_range.byte_offset = byte_offset
    mocked_transferable_range.transferable.id = str(a_uuid)

    function_to_call = functools.partial(
        transferable_range._assert_no_transferable_ranges_were_missed,
        mocked_transferable_range,
        mocked_transferable,
    )

    if expected_exception is None:
        function_to_call()
    else:
        with pytest.raises(expected_exception):
            function_to_call()


@pytest.mark.parametrize("state", set(IncomingTransferableState))
@pytest.mark.django_db()
def test__transferable_is_ready(state: IncomingTransferableState):
    if state.is_final:
        with pytest.raises(transferable_range.TransferableAlreadyInFinalState):
            transferable_range._assert_transferable_is_ready(factory.IncomingTransferableFactory(state=state))
    else:
        transferable_range._assert_transferable_is_ready(factory.IncomingTransferableFactory(state=state))


@pytest.mark.parametrize(
    (
        "transferable_bytes_received",
        "transferable_size",
        "transferable_range_size",
        "transferable_range_transferable_size",
        "expected_exception",
        "expect_warning",
    ),
    [
        # First TransferableRange, half the total Transferable
        (0, 4, 2, 4, transferable_range.FinalSizeMismatchError, False),
        # First TransferableRange containing all the data
        (0, 2, 2, 2, None, False),
        # First TransferableRange containing all the data, wrong size
        (0, 1, 2, 2, None, True),
        # First TransferableRange containing more than all the data
        # (this should not be possible)
        (0, None, 4, 2, transferable_range.FinalSizeMismatchError, False),
        # TransferableRange containing all the data when it has already been received
        (2, None, 2, 2, transferable_range.FinalSizeMismatchError, False),
        # Last TransferableRange received while having already received the only
        # other TransferableRange
        (2, None, 2, 4, None, False),
        # Last TransferableRange received while having already received the only
        # other TransferableRange, wrong size
        (2, 1, 2, 4, None, True),
    ],
)
def test__assert_transferable_size_is_consistent(
    transferable_bytes_received: int,
    transferable_size: int,
    transferable_range_size: int,
    transferable_range_transferable_size: int,
    expected_exception: transferable_range.FinalSizeMismatchError | None,
    expect_warning: bool,
    faker: Faker,
    caplog: pytest.LogCaptureFixture,
):
    caplog.set_level(logging.WARNING)

    mocked_transferable = mock.create_autospec(models.IncomingTransferable)
    mocked_transferable.bytes_received = transferable_bytes_received
    mocked_transferable.size = transferable_size

    a_uuid = faker.uuid4()
    # mock.create_autospec does not seem to work for class attributes
    mocked_transferable_range = mock.Mock()
    mocked_transferable_range.data = b"0" * transferable_range_size
    mocked_transferable_range.transferable.size = transferable_range_transferable_size
    mocked_transferable_range.transferable.id = str(a_uuid)

    function_to_call = functools.partial(
        transferable_range._assert_transferable_size_is_consistent,
        mocked_transferable_range,
        mocked_transferable,
    )

    if expected_exception is None:
        function_to_call()
    else:
        with pytest.raises(expected_exception):
            function_to_call()

    if expect_warning:
        assert "incoming_transferable_size_mismatch" in caplog.text


@pytest.mark.parametrize(
    (
        "expected_computed_sha1",
        "transferable_sha1_string",
        "expected_exception",
    ),
    [
        # correct hash
        (
            hashlib.sha1(b"I like waffles"),
            bytes.fromhex("b761f36a6be4e40ac70ccc5c93b21775d1a99fc3"),
            None,
        ),
        # incorrect hash
        (
            hashlib.sha1(b"Small deeds done are better than great deeds planned."),
            bytes.fromhex("b761f36a6be4e40ac70ccc5c93b21775d1a99fc3"),
            transferable_range.FinalDigestMismatchError,
        ),
    ],
)
def test__assert_transferable_sha1_is_consistent(
    expected_computed_sha1: "hashlib._Hash",
    transferable_sha1_string: str,
    expected_exception: transferable_range.FinalDigestMismatchError | None,
    faker: Faker,
):
    a_uuid = faker.uuid4()
    # mock.create_autospec does not seem to work for class attributes
    mocked_transferable_range = mock.Mock()
    mocked_transferable_range.transferable.id = str(a_uuid)
    mocked_transferable_range.transferable.sha1 = transferable_sha1_string

    function_to_call = functools.partial(
        transferable_range._assert_transferable_sha1_is_consistent,
        mocked_transferable_range,
        expected_computed_sha1,
    )

    if expected_exception is None:
        function_to_call()
    else:
        with pytest.raises(expected_exception):
            function_to_call()


@pytest.mark.django_db()
def test__extract_data():
    data = b"hello "
    sha1 = hashlib.sha1()
    sha1.update(data)
    sha1_intermediary = rehash.sha1_to_bytes(sha1)
    mocked_transferable_range = mock.Mock()
    mocked_transferable_range.data = b"world!"

    transferable = factory.IncomingTransferableFactory(
        rehash_intermediary=sha1_intermediary,
        state=models.IncomingTransferableState.ONGOING,
    )
    data, new_sha1 = transferable_range._extract_data(mocked_transferable_range, transferable)

    sha1.update(mocked_transferable_range.data)
    assert sha1.digest() == new_sha1.digest()
