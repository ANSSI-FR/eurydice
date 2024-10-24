import hashlib
import logging
from typing import Optional

import humanfriendly as hf
import pytest
from faker import Faker

from eurydice.common import minio
from eurydice.destination.core import models
from eurydice.destination.receiver.packet_handler import extractors
from eurydice.destination.utils import rehash
from tests.common.integration import factory as common_factory
from tests.destination.integration import factory as destination_factory
from tests.destination.integration.utils import s3 as s3_utils


@pytest.mark.django_db()
def test_transferable_range_extractor_success():
    extractor = extractors.TransferableRangeExtractor()

    first_transferable_range_data = b"0" * hf.parse_size("5MiB")

    transferable_range = common_factory.TransferableRangeFactory(
        transferable=common_factory.TransferableFactory(sha1=None, size=None),
        byte_offset=0,
        data=first_transferable_range_data,
        is_last=False,
    )

    packet = common_factory.OnTheWirePacketFactory(
        transferable_ranges=[transferable_range]
    )

    extractor.extract(packet)

    all_transferables = models.IncomingTransferable.objects.all()

    assert all_transferables.count() == 1

    queried_transferable = all_transferables.first()

    assert queried_transferable.id == transferable_range.transferable.id
    assert queried_transferable.state == models.IncomingTransferableState.ONGOING
    assert queried_transferable.bytes_received == len(transferable_range.data)
    assert queried_transferable.size is None
    assert bytes(queried_transferable.rehash_intermediary) == rehash.sha1_to_bytes(
        hashlib.sha1(transferable_range.data)
    )
    assert queried_transferable.finished_at is None
    assert queried_transferable.sha1 is None

    assert s3_utils.multipart_upload_exists(queried_transferable)

    final_transferable_range_data = b"0" * hf.parse_size("5KiB")
    final_transferable_sha1 = hashlib.sha1(
        transferable_range.data + final_transferable_range_data
    )
    final_transferable_size = len(first_transferable_range_data) + len(
        final_transferable_range_data
    )

    another_transferable_range = common_factory.TransferableRangeFactory(
        transferable=common_factory.TransferableFactory(
            id=queried_transferable.id,
            user_profile_id=(
                queried_transferable.user_profile.associated_user_profile_id
            ),
            sha1=final_transferable_sha1.digest(),
            size=final_transferable_size,
        ),
        data=final_transferable_range_data,
        is_last=True,
        byte_offset=queried_transferable.bytes_received,
    )

    packet = common_factory.OnTheWirePacketFactory(
        transferable_ranges=[another_transferable_range]
    )

    extractor.extract(packet)

    all_transferables = models.IncomingTransferable.objects.all()

    assert all_transferables.count() == 1

    queried_transferable = all_transferables.first()

    assert queried_transferable.id == transferable_range.transferable.id
    assert queried_transferable.state == models.IncomingTransferableState.SUCCESS
    assert queried_transferable.bytes_received == final_transferable_size
    assert queried_transferable.size == final_transferable_size
    assert bytes(queried_transferable.rehash_intermediary) == rehash.sha1_to_bytes(
        final_transferable_sha1
    )
    assert queried_transferable.finished_at is not None
    assert bytes(queried_transferable.sha1) == final_transferable_sha1.digest()

    response = None
    try:
        response = minio.client.get_object(
            bucket_name=queried_transferable.s3_bucket_name,
            object_name=queried_transferable.s3_object_name,
        )
        data = response.read()
    finally:
        if response:
            response.close()
            response.release_conn()

    assert data == first_transferable_range_data + final_transferable_range_data


@pytest.mark.django_db()
@pytest.mark.parametrize("transferable_range_size", ["1B", "1KiB", "4.99KiB"])
def test_transferable_range_extractor_success_small_transferable_range(
    transferable_range_size: str,
):
    extractor = extractors.TransferableRangeExtractor()

    transferable_range_size = hf.parse_size(transferable_range_size)
    transferable_range_data = b"0" * transferable_range_size
    transferable_range_digest = hashlib.sha1(transferable_range_data)

    transferable_range = common_factory.TransferableRangeFactory(
        transferable=common_factory.TransferableFactory(
            sha1=transferable_range_digest.digest(),
            size=transferable_range_size,
        ),
        byte_offset=0,
        data=transferable_range_data,
        is_last=True,
    )

    packet = common_factory.OnTheWirePacketFactory(
        transferable_ranges=[transferable_range]
    )

    extractor.extract(packet)

    all_transferables = models.IncomingTransferable.objects.all()

    assert all_transferables.count() == 1

    queried_transferable = all_transferables.first()

    assert queried_transferable.id == transferable_range.transferable.id
    assert queried_transferable.state == models.IncomingTransferableState.SUCCESS
    assert queried_transferable.bytes_received == transferable_range_size
    assert queried_transferable.size == transferable_range_size
    assert bytes(queried_transferable.rehash_intermediary) == rehash.sha1_to_bytes(
        transferable_range_digest
    )
    assert queried_transferable.finished_at is not None
    assert bytes(queried_transferable.sha1) == transferable_range_digest.digest()
    assert queried_transferable.s3_upload_parts.count() == 0

    response = None
    try:
        response = minio.client.get_object(
            bucket_name=queried_transferable.s3_bucket_name,
            object_name=queried_transferable.s3_object_name,
        )
        data = response.read()
    finally:
        if response:
            response.close()
            response.release_conn()

    assert data == transferable_range_data


@pytest.mark.django_db()
def test_transferable_range_extractor_missed_transferable_range(faker: Faker):
    extractor = extractors.TransferableRangeExtractor()

    transferable_range = common_factory.TransferableRangeFactory(
        byte_offset=faker.pyint(min_value=2)
    )
    packet = common_factory.OnTheWirePacketFactory(
        transferable_ranges=[transferable_range]
    )

    extractor.extract(packet)

    queried_transferable = models.IncomingTransferable.objects.get(
        id=transferable_range.transferable.id
    )

    assert queried_transferable.state == models.IncomingTransferableState.ERROR
    assert queried_transferable.finished_at is not None


@pytest.mark.django_db()
def test_transferable_range_transferable_already_marked_as_error(
    caplog: pytest.LogCaptureFixture,
):
    incoming_transferable = destination_factory.IncomingTransferableFactory(
        bytes_received=1024, size=2048, state=models.IncomingTransferableState.ERROR
    )
    transferable_range = common_factory.TransferableRangeFactory(
        transferable=common_factory.TransferableFactory(id=incoming_transferable.id),
        byte_offset=incoming_transferable.bytes_received,
    )
    packet = common_factory.OnTheWirePacketFactory(
        transferable_ranges=[transferable_range]
    )

    extractor = extractors.TransferableRangeExtractor()
    extractor.extract(packet)

    assert caplog.messages[0] == f"Extracting data for {incoming_transferable.id}"
    assert caplog.messages[1] == (
        f"IncomingTransferable {incoming_transferable.id} has state ERROR. "
        "Ignoring the associated transferable range received."
    )


@pytest.mark.django_db()
@pytest.mark.parametrize(
    ("actual_transferable_size", "reported_transferable_size"),
    [
        ("4KiB", "3KiB"),
        ("3KiB", "4KiB"),
        ("10KiB", "15KiB"),
        ("15KiB", "10KiB"),
    ],
)
def test_transferable_range_extractor_new_transferable_size_mismatch(
    actual_transferable_size: str,
    reported_transferable_size: Optional[str],
    caplog: pytest.LogCaptureFixture,
):
    caplog.set_level(logging.ERROR)
    extractor = extractors.TransferableRangeExtractor()

    transferable_range_size = hf.parse_size(actual_transferable_size)
    transferable_range_data = b"0" * transferable_range_size
    transferable_range_digest = hashlib.sha1(transferable_range_data)

    transferable_size = hf.parse_size(reported_transferable_size)

    transferable_range = common_factory.TransferableRangeFactory(
        transferable=common_factory.TransferableFactory(
            sha1=transferable_range_digest.digest(), size=transferable_size
        ),
        byte_offset=0,
        data=transferable_range_data,
        is_last=True,
    )

    packet = common_factory.OnTheWirePacketFactory(
        transferable_ranges=[transferable_range]
    )

    extractor.extract(packet)

    assert (
        f"Received {hf.format_size(len(transferable_range_data))}, "
        f"expected {hf.format_size(transferable_size)} "
        f"for Transferable {transferable_range.transferable.id}"
    ) in caplog.text

    queried_transferable = models.IncomingTransferable.objects.get(
        id=transferable_range.transferable.id
    )

    assert queried_transferable.state == models.IncomingTransferableState.ERROR
    assert queried_transferable.finished_at is not None


@pytest.mark.django_db()
@pytest.mark.parametrize(
    "reported_sha1",
    [
        b"\xc6\xa8\x82F\x0c\xadFrU\xaf\x1dx\xda\r\xea?\xdc\xd3V\x93",
    ],
)
def test_transferable_range_extractor_new_transferable_digest_mismatch(
    reported_sha1: bytes, caplog: pytest.LogCaptureFixture, faker: Faker
):
    caplog.set_level(logging.ERROR)
    extractor = extractors.TransferableRangeExtractor()

    transferable_range_data = faker.binary(10)

    transferable_range = common_factory.TransferableRangeFactory(
        transferable=common_factory.TransferableFactory(
            sha1=reported_sha1, size=len(transferable_range_data)
        ),
        byte_offset=0,
        data=transferable_range_data,
        is_last=True,
    )

    packet = common_factory.OnTheWirePacketFactory(
        transferable_ranges=[transferable_range]
    )

    extractor.extract(packet)

    assert f"expected {reported_sha1.hex()}" in caplog.text
    assert str(transferable_range.transferable.id) in caplog.text

    queried_transferable = models.IncomingTransferable.objects.get(
        id=transferable_range.transferable.id
    )

    assert queried_transferable.state == models.IncomingTransferableState.ERROR
    assert queried_transferable.finished_at is not None


@pytest.mark.django_db()
@pytest.mark.parametrize(
    "reported_sha1",
    [b"\x03\xd7\x03,@No\x92\x8b\\\xf2\xa5\xb5\xb4\x06\x02\xd0\t\x19\xc9"],
)
def test_transferable_range_extractor_existing_transferable_digest_mismatch(
    reported_sha1: bytes,
):
    extractor = extractors.TransferableRangeExtractor()

    first_transferable_range_data = b"0" * hf.parse_size("5KiB")

    transferable_range = common_factory.TransferableRangeFactory(
        transferable=common_factory.TransferableFactory(
            sha1=None, size=2 * hf.parse_size("5KiB")
        ),
        byte_offset=0,
        data=first_transferable_range_data,
        is_last=False,
    )

    packet = common_factory.OnTheWirePacketFactory(
        transferable_ranges=[transferable_range]
    )

    extractor.extract(packet)

    all_transferables = models.IncomingTransferable.objects.all()

    assert all_transferables.count() == 1

    queried_transferable = all_transferables.first()

    assert queried_transferable.id == transferable_range.transferable.id
    assert queried_transferable.state == models.IncomingTransferableState.ONGOING
    assert queried_transferable.bytes_received == len(transferable_range.data)
    assert queried_transferable.size == 2 * hf.parse_size("5KiB")
    assert bytes(queried_transferable.rehash_intermediary) == rehash.sha1_to_bytes(
        hashlib.sha1(transferable_range.data)
    )
    assert queried_transferable.finished_at is None
    assert queried_transferable.sha1 is None

    assert s3_utils.multipart_upload_exists(queried_transferable)

    final_transferable_range_data = b"0" * hf.parse_size("5KiB")

    another_transferable_range = common_factory.TransferableRangeFactory(
        transferable=common_factory.TransferableFactory(
            id=queried_transferable.id,
            user_profile_id=(
                queried_transferable.user_profile.associated_user_profile_id
            ),
            sha1=reported_sha1,
            size=2 * hf.parse_size("5KiB"),
        ),
        data=final_transferable_range_data,
        is_last=True,
        byte_offset=queried_transferable.bytes_received,
    )

    packet = common_factory.OnTheWirePacketFactory(
        transferable_ranges=[another_transferable_range]
    )

    extractor.extract(packet)

    all_transferables = models.IncomingTransferable.objects.all()

    assert all_transferables.count() == 1

    queried_transferable = all_transferables.first()

    assert queried_transferable.state == models.IncomingTransferableState.ERROR
    assert queried_transferable.finished_at is not None

    assert not s3_utils.multipart_upload_exists(queried_transferable)


@pytest.mark.django_db()
@pytest.mark.parametrize(
    ("actual_transferable_size", "reported_transferable_size"),
    [
        ("4KiB", "3KiB"),
        ("3KiB", "4KiB"),
        ("6KiB", "7KiB"),
        ("7KiB", "6KiB"),
    ],
)
def test_transferable_range_extractor_existing_transferable_size_mismatch(
    actual_transferable_size: str,
    reported_transferable_size: str,
):
    extractor = extractors.TransferableRangeExtractor()

    first_transferable_range_size = hf.parse_size(actual_transferable_size) // 2
    first_transferable_range_data = b"0" * first_transferable_range_size

    transferable_range = common_factory.TransferableRangeFactory(
        transferable=common_factory.TransferableFactory(sha1=None, size=None),
        byte_offset=0,
        data=first_transferable_range_data,
        is_last=False,
    )

    packet = common_factory.OnTheWirePacketFactory(
        transferable_ranges=[transferable_range]
    )

    extractor.extract(packet)

    all_transferables = models.IncomingTransferable.objects.all()

    assert all_transferables.count() == 1

    queried_transferable = all_transferables.first()

    assert queried_transferable.id == transferable_range.transferable.id
    assert queried_transferable.state == models.IncomingTransferableState.ONGOING
    assert queried_transferable.bytes_received == len(transferable_range.data)
    assert bytes(queried_transferable.rehash_intermediary) == rehash.sha1_to_bytes(
        hashlib.sha1(transferable_range.data)
    )
    assert queried_transferable.finished_at is None
    assert queried_transferable.sha1 is None

    assert s3_utils.multipart_upload_exists(queried_transferable)

    reported_final_transferable_size = hf.parse_size(reported_transferable_size)
    final_transferable_range_size = (
        hf.parse_size(actual_transferable_size) - first_transferable_range_size
    )
    final_transferable_range_data = b"0" * final_transferable_range_size

    another_transferable_range = common_factory.TransferableRangeFactory(
        transferable=common_factory.TransferableFactory(
            id=queried_transferable.id,
            user_profile_id=(
                queried_transferable.user_profile.associated_user_profile_id
            ),
            sha1=hashlib.sha1(
                first_transferable_range_data + final_transferable_range_data
            ).digest(),
            size=reported_final_transferable_size,
        ),
        data=final_transferable_range_data,
        is_last=True,
        byte_offset=queried_transferable.bytes_received,
    )

    packet = common_factory.OnTheWirePacketFactory(
        transferable_ranges=[another_transferable_range]
    )

    extractor.extract(packet)

    all_transferables = models.IncomingTransferable.objects.all()

    assert all_transferables.count() == 1

    queried_transferable = all_transferables.first()

    assert queried_transferable.state == models.IncomingTransferableState.ERROR
    assert queried_transferable.finished_at is not None

    assert not s3_utils.multipart_upload_exists(queried_transferable)
