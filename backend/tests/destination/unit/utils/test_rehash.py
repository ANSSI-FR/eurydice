import hashlib

import humanfriendly as hf
import hypothesis
from hypothesis import strategies

from eurydice.destination.utils import rehash


@hypothesis.given(strategies.binary(max_size=hf.parse_size("10 MB")))
@hypothesis.example(b"")
def test_sha1_to_bytes_success(data: bytes):
    sha1 = hashlib.sha1()
    sha1.update(data)
    assert isinstance(rehash.sha1_to_bytes(sha1), bytes)


@hypothesis.given(strategies.binary(max_size=hf.parse_size("10 MB")))
@hypothesis.example(b"")
def test_sha1_to_bytes_from_bytes_success(data: bytes):
    sha1 = hashlib.sha1()
    sha1.update(data)

    dump = rehash.sha1_to_bytes(sha1)
    assert rehash.sha1_from_bytes(dump).digest() == sha1.digest()


@hypothesis.given(
    strategies.binary(max_size=hf.parse_size("1 MB")),
    strategies.integers(max_value=50),
)
def test_sha1_to_bytes_from_bytes_success_multiple_steps_success(data: bytes, steps: int):
    sha1 = hashlib.sha1()
    dump = rehash.sha1_to_bytes(sha1)

    for _ in range(steps):
        resumed_sha1 = rehash.sha1_from_bytes(dump)

        resumed_sha1.update(data)
        sha1.update(data)

        assert resumed_sha1.digest() == sha1.digest()
        dump = rehash.sha1_to_bytes(resumed_sha1)
