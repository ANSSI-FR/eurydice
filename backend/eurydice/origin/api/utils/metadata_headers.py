"""
Misc. utilities for handling User submitted metadata alongside
a Transferable's content in the form of HTTP Headers.
"""

from django.conf import settings
from django.http import request


def extract_metadata_from_headers(headers: request.HttpHeaders) -> dict[str, str]:
    """Extract user provided metadata in HTTP headers

    Args:
        headers: HTTP header name/value mapping

    Returns:
        Metadata HTTP header name/value mapping
    """
    return {
        header_name: header_value
        for header_name, header_value in headers.items()
        # Header names should be case insensitive
        # https://stackoverflow.com/a/5259004
        if header_name.startswith(settings.METADATA_HEADER_PREFIX)
    }


NEEDED_METADATA = [
    "Metadata-Encrypted-Size",
    "Metadata-Encrypted",
    "Metadata-Parts-Count",
    "Metadata-Main-Part-Size",
    "Metadata-Last-Part-Size",
    "Metadata-Encrypted-Symmetric-Key",
    "Metadata-Header",
]


def is_metadata_for_multipart_upload_complete(metadata: dict) -> bool:
    """To know if all needed metadata are inside the metadata keys

    Args:
        metadata: the metadata received in the request

    Returns:
        True if all needed metadata are in the received metadata headers,
             False otherwise

    """
    return all(key in metadata for key in NEEDED_METADATA)
