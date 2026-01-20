import hashlib
import io

import pytest
from faker import Faker

from eurydice.origin.api.utils import PartitionedStream
from tests import utils

TEST_PARAMS = [
    # test when stream_partition_size == len(bytes)
    (
        bytes("reality must take precedence over public relations", "utf-8"),
        50,
    ),
    # test when stream_partition_size > len(bytes)
    (
        bytes("reality must take precedence over public relations", "utf-8"),
        utils.fake.pyint(min_value=51),
    ),
    # test when stream_partition_size < len(bytes)
    (
        bytes("reality must take precedence over public relations", "utf-8"),
        utils.fake.pyint(min_value=1, max_value=49),
    ),
    # test random bytes with random stream_partition_size
    (
        utils.fake.binary(utils.fake.pyint(min_value=1, max_value=20)),
        utils.fake.pyint(),
    ),
]


@pytest.mark.parametrize(("random_bytes", "stream_partition_size"), TEST_PARAMS)
def test_partitioned_stream_full(random_bytes: bytes, stream_partition_size: int):
    """
    Assert all bytes inputted are read correctly
    """

    stream = io.BytesIO(random_bytes)

    all_read_bytes = b""

    for partition in PartitionedStream(stream, stream_partition_size):
        all_read_bytes += partition.read()

    assert all_read_bytes == random_bytes


def test_partitioned_stream_digest_update(faker: Faker):
    """
    Assert the Stream's digest is computed correctly accross multiple SubStreams
    """
    random_bytes = faker.binary(faker.pyint(min_value=2, max_value=20))

    # random stream part size
    # capped to ensure at least 2 partitioned_streams are used
    stream_partition_size = faker.pyint(max_value=len(random_bytes) - 1)

    stream = io.BytesIO(random_bytes)

    stream_digest = hashlib.sha1()

    for partition in PartitionedStream(stream, stream_partition_size, stream_digest.update):
        partition.read()

    assert stream_digest.hexdigest() == hashlib.sha1(random_bytes).hexdigest()


@pytest.mark.parametrize(("random_bytes", "stream_partition_size"), TEST_PARAMS)
def test_partitioned_stream_default_chunk_size(random_bytes: bytes, stream_partition_size: int):
    """
    Assert .read()  method's chunk_size argument defaults to
    the correct value (ie: stream_partition_size)
    """
    stream = io.BytesIO(random_bytes)

    stream_partition = next(iter(PartitionedStream(stream, stream_partition_size)))

    if stream_partition_size > len(random_bytes):
        assert len(stream_partition.read()) == len(random_bytes)
    else:
        assert len(stream_partition.read()) == stream_partition_size


def test_partitioned_stream_chunk_size(faker: Faker):
    """
    Assert .read()  method's chunk_size argument returns the correct number of bytes
    """
    random_bytes = b"Les requetes trop rapides"
    stream = io.BytesIO(random_bytes)

    stream_partition = next(iter(PartitionedStream(stream, len(random_bytes))))

    assert len(stream_partition.read(0)) == 0

    read_chunk_size = faker.pyint(max_value=len(random_bytes) - 1)

    bytes_read = stream_partition.read(read_chunk_size)

    assert len(bytes_read) == read_chunk_size

    bytes_read += stream_partition.read()

    assert bytes_read == random_bytes


def test_partitioned_stream__partition_eof():
    """
    Assert partitioned_stream._partition_eof is toggled when `partition_size` bytes
    have been read
    """
    random_bytes = bytes("Les requetes trop rapides", "utf-8")
    stream = io.BytesIO(random_bytes)

    stream_partition = next(iter(PartitionedStream(stream, len(random_bytes))))
    read_chunk_size = len(random_bytes)

    assert stream_partition._partition_eof is False
    assert stream_partition.read(read_chunk_size) == random_bytes
    assert stream_partition._partition_eof is True
