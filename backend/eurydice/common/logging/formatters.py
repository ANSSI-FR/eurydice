import json
import logging
from typing import Any
from typing import Union

from django.http import HttpRequest


def json_django_http_request(obj: HttpRequest) -> dict:
    """Serializes a Django HttpRequest into a smaller dict."""

    as_dict = obj.__dict__

    return {
        "META": {
            k: v for k, v in as_dict.get("META", {}).items() if not k.startswith("wsgi")
        },
        "user": as_dict.get("user"),
        "COOKIES": as_dict.get("COOKIES"),
    }


def json_default(obj: Any) -> Union[str, dict]:
    """Serializes an object into a dict, or a string representation of the object."""
    if isinstance(obj, HttpRequest):
        return json_django_http_request(obj)

    return str(obj)


class JSONFormatter(logging.Formatter):
    """Formats LogRecords into json-formatted strings."""

    def format(self, record: logging.LogRecord) -> str:
        """Serializes a log record into a json string"""
        return json.dumps(self._record_to_dict(record), default=json_default)

    def _record_to_dict(self, record: logging.LogRecord) -> dict:
        """Formats a log record into a dict"""
        unwanted_elements = {"processName", "threadName"}

        as_dict = {
            key: value
            for key, value in record.__dict__.items()
            if key not in unwanted_elements
        }

        if "message" not in as_dict:
            args = as_dict["args"] or {}
            as_dict["message"] = as_dict["msg"] % args

        return as_dict
