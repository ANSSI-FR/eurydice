"""Converts bytes into human readable words (or words back into bytes)
using a fixed set of words, defined in a given plain text file.

Two bytes = one word.

For example from 16 bytes, 8 words will be generated like this:
"prudemment brillants silly prealables CITROEN ilknur mare SOUPCONNES"

"""

import pathlib
import re
from typing import Dict
from typing import List
from typing import Literal

from django.conf import settings

_BYTE_ORDER: Literal["big"] = "big"

_DEFAULT_WORDLIST_PATH: pathlib.Path = (
    pathlib.Path(__file__).resolve().parent / "word_list.txt"
)
_WORDLIST_PATH: str = getattr(settings, "BYTES2WORDS_DICT", str(_DEFAULT_WORDLIST_PATH))

# List of words in the file
_WORDS: List[str] = pathlib.Path(_WORDLIST_PATH).read_text().split("\n")

# From a word, retrieves the index of that word in _WORDS
_INDEX: Dict[str, int] = {word: i for i, word in enumerate(_WORDS)}

_NON_ALPHANUMERIC = r"[^a-zA-Z]+"

_SEPARATOR = " "


class EncodingError(ValueError):
    """Signal an error during the encoding process."""


class DecodingError(ValueError):
    """Signal an error during the decoding process."""


def encode(data: bytes) -> str:
    """Converts bytes into a string of readable words.
    Data must be of even length.

    Splits the given data into groups of two bytes. (0x12345678 -> 0x1234, 0x5678)
        For each group of two bytes,
        casts those two bytes into an int,              (0x1234 -> 4660)
        and uses that int as an index to pick a word from the
        list of words defined in the constructor        (self._words[4660])
    Glues all the picked words together with spaces.

    Args:
        data: bytes of even length (ie. len(data) % 2 == 0)

    Returns:
        String of x words. (x = len(data) / 2)

    Raises:
        ValueError: If len(data) is not a multiple of 2.

    """
    if len(data) % 2 != 0:
        raise EncodingError("Data length must be even.")

    return _SEPARATOR.join(
        [
            _WORDS[int.from_bytes(data[i * 2 : i * 2 + 2], _BYTE_ORDER)]
            for i in range(int(len(data) / 2))
        ]
    )


def decode(words: str) -> bytes:
    """Converts words back into bytes.

    For each word, retrieves its index as an int,
    converts the index into 2 bytes, and glues all those bytes together.

    Args:
        words: A string of space-separated words

    Returns:
        bytes

    """

    decoded_bytes = []
    for word in re.split(_NON_ALPHANUMERIC, words):
        try:
            position = _INDEX[word]
        except KeyError:
            raise DecodingError(f"Word '{word}' cannot be found in the index.")
        else:
            decoded_bytes.append(position.to_bytes(2, _BYTE_ORDER))

    return b"".join(decoded_bytes)


__all__ = ("encode", "decode", "EncodingError", "DecodingError")
