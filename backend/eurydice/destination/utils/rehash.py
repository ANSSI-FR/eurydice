"""Utility functions to dump and load the internal state of a hashlib.sha1 object.

Requirements: OpenSSL >1.1.0 and Python 3.8+

Adapted from:
    - https://github.com/kislyuk/rehash/blob/f1169d2adf150cf9f95717c5aa6945fba9137720/rehash/structs.py  # noqa: E501
    - https://github.com/kislyuk/rehash/blob/f1169d2adf150cf9f95717c5aa6945fba9137720/rehash/__init__.py  # noqa: E501

"""

# pytype: disable=invalid-typevar  # noqa: E800

import ctypes
import hashlib


# https://github.com/openssl/openssl/blob/master/crypto/evp/evp_local.h#L18-L33
class EVP_MD_CTX(ctypes.Structure):  # noqa: N801
    _fields_ = [
        ("digest", ctypes.c_void_p),
        ("engine", ctypes.c_void_p),
        ("flags", ctypes.c_ulong),
        ("md_data", ctypes.POINTER(ctypes.c_char)),
    ]


# https://github.com/python/cpython/blob/master/Modules/_hashopenssl.c#L68-L72
class EVPobject(ctypes.Structure):
    _fields_ = [
        ("ob_refcnt", ctypes.c_size_t),
        ("ob_type", ctypes.c_void_p),
        ("ctx", ctypes.POINTER(EVP_MD_CTX)),
    ]


# The size of hashlib's internal data C buffer for a SHA-1
SHA1_HASHLIB_BUFSIZE: int = 104


# hashlib._Hash is a stub-only construct. To use it in live code, quote it.
# See https://github.com/python/typeshed/issues/2928#issuecomment-487889925
def sha1_to_bytes(sha1_hashlib: "hashlib._Hash") -> bytes:
    """Dump the internal state of a hashlib.sha1 object.

    Args:
        sha1_hashlib: the hashlib object.

    Returns:
        The bytes corresponding to the internal state of the hashlib object.

    """
    raw = ctypes.cast(ctypes.c_void_p(id(sha1_hashlib)), ctypes.POINTER(EVPobject))
    return raw.contents.ctx.contents.md_data[  # pytype: disable=attribute-error
        :SHA1_HASHLIB_BUFSIZE
    ]


def sha1_from_bytes(data: bytes) -> "hashlib._Hash":
    """Load a hashlib.sha1 object from bytes.

    Args:
        data: bytes to initialize the hashlib.sha1 object with.

    Returns:
        An initialized hashlib.sha1.

    """
    sha1_hashlib = hashlib.sha1()  # nosec
    raw = ctypes.cast(ctypes.c_void_p(id(sha1_hashlib)), ctypes.POINTER(EVPobject))
    ctypes.memmove(
        raw.contents.ctx.contents.md_data,  # pytype: disable=attribute-error
        data,
        SHA1_HASHLIB_BUFSIZE,
    )
    return sha1_hashlib


__all__ = ("sha1_to_bytes", "sha1_from_bytes", "SHA1_HASHLIB_BUFSIZE")
