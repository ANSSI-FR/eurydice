import logging
from typing import Optional
from unittest import mock

import pytest
from django.conf import Settings

from eurydice.origin.api import exceptions
from eurydice.origin.api.views import outgoing_transferable


def test__get_content_length_transfer_encoding_chunked(
    caplog: pytest.LogCaptureFixture,
):
    caplog.set_level(logging.WARNING)

    request = mock.Mock()
    request.headers = {"Transfer-Encoding": "chunked", "Content-Length": "1"}

    assert outgoing_transferable._get_content_length(request) is None
    assert caplog.messages == [
        "Cannot retrieve the 'Content-Length' header of an HTTP request "
        "using chunked transfer encoding."
    ]


@pytest.mark.parametrize(
    ("content_length_header", "transferable_max_size", "expected_result"),
    [
        (None, 10, None),
        ("1", 2, 1),
        (
            "2",
            1,
            exceptions.RequestEntityTooLargeError,
        ),
        ("foo", 1, exceptions.InvalidContentLengthError),
        ("-5", 1, None),
    ],
)
def test__get_content_length(
    content_length_header: str,
    transferable_max_size: int,
    expected_result: Optional[Exception],
    settings: Settings,
):
    request = mock.Mock()
    if content_length_header:
        request.headers = {"Content-Length": content_length_header}
    else:
        request.headers = {}

    settings.TRANSFERABLE_MAX_SIZE = transferable_max_size

    if isinstance(expected_result, type(Exception)):
        with pytest.raises(expected_result):
            outgoing_transferable._get_content_length(request)
    elif expected_result is None:
        assert outgoing_transferable._get_content_length(request) is None
    else:
        assert outgoing_transferable._get_content_length(request) == expected_result
