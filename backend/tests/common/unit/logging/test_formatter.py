import io
from logging import LogRecord

import pytest
from django.core.handlers.wsgi import WSGIRequest

from eurydice.common.logging import JSONFormatter


@pytest.mark.parametrize(
    "value",
    [
        LogRecord("name", 20, "path", 1, "message", None, None),
        LogRecord(
            "name",
            20,
            "path",
            1,
            "message %s",
            ["args"],
            {"exc_info": "exc_info"},
            "func",
            "sinfo",
        ),
        LogRecord(
            "name",
            20,
            "path",
            1,
            "message %s",
            [{"deep": {"but": "still", "just": "a dict"}}],
            {"exc_info": "exc_info"},
            "func",
            "sinfo",
        ),
        LogRecord(
            "name",
            20,
            "path",
            1,
            "message %s",
            [WSGIRequest({"REQUEST_METHOD": "GET", "wsgi.input": io.BytesIO()})],
            WSGIRequest({"REQUEST_METHOD": "GET", "wsgi.input": io.BytesIO()}),
            "func",
            "sinfo",
        ),
        LogRecord(
            "name",
            20,
            "path",
            1,
            "message %s",
            [Exception(Exception("test"))],
            Exception(Exception("test")),
            "func",
            "sinfo",
        ),
    ],
)
def test_formatter_can_format(value: LogRecord):
    assert JSONFormatter().format(value) is not None

    # Depending on the default formatter, value.message may not
    # have been set. Test both with and without
    # https://github.com/python/cpython/blob/26fa25a9a73f0e31bf0f0d94103fa4de38c0a3cc/Lib/logging/__init__.py#L678  # noqa: E501
    value.message = value.getMessage()
    assert JSONFormatter().format(value) is not None
