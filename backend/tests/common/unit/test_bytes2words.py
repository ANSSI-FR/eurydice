import hashlib

import pytest
from faker import Faker

from eurydice.common import bytes2words


@pytest.mark.parametrize(
    "value",
    [
        hashlib.sha256((0).to_bytes(4, "big")).digest(),
        hashlib.sha256((1).to_bytes(4, "big")).digest(),
        hashlib.sha256((2).to_bytes(4, "big")).digest(),
        hashlib.sha256((3).to_bytes(4, "big")).digest(),
        hashlib.sha256((4).to_bytes(4, "big")).digest(),
        b"\x00\x00\xff\xff",
        b"\x00\x00\x00\x00",
    ],
)
def test_encode_decode_success(value: bytes):
    assert bytes2words.decode(bytes2words.encode(value)) == value


@pytest.mark.parametrize("length", [2, 4, 6, 8, 16, 32, 64, 66])
def test_encode_decode_success_even_length(length: int):
    value = bytes.fromhex("00" * length)
    assert bytes2words.decode(bytes2words.encode(value)) == value


@pytest.mark.parametrize("length", [1, 3, 5, 99])
def test_encode_error_odd_length(length: int):
    value = bytes.fromhex("00" * length)
    with pytest.raises(bytes2words.EncodingError, match="Data length must be even."):
        bytes2words.encode(value)


@pytest.mark.parametrize("separator", [" ", "  ", "-"])
def test_decode_separator(separator: str, faker: Faker):
    value = faker.binary(6)
    token = bytes2words.encode(value)

    token_with_different_separator = token.replace(" ", separator)

    assert bytes2words.decode(token_with_different_separator) == value


@pytest.mark.parametrize(
    "words",
    [
        "abusif potatoe",
        "Forasuccessfultechnologyrealitymusttakeprecedenceoverpublicrelations",
    ],
)
def test_decode_error_unknown_word(words: str):
    with pytest.raises(
        bytes2words.DecodingError, match=r".*cannot be found in the index"
    ):
        bytes2words.decode(words)
