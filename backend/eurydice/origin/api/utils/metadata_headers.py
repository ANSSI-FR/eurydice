"""
Misc. utilities for handling User submitted metadata alongside
a Transferable's content in the form of HTTP Headers.
"""

from typing import Dict

from django.conf import settings
from django.http import request


def extract_metadata_from_headers(headers: request.HttpHeaders) -> Dict[str, str]:
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
