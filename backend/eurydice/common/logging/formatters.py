import hashlib
import io
import json
import logging.handlers
import time
import traceback
from base64 import b64encode
from types import TracebackType
from typing import Any

UNWANTED_LOG_KEYS = (
    "processName",
    "threadName",
    "exc_text",
    "color_message",
)


class JSONFormatter(logging.Formatter):
    """Formats LogRecords into json-formatted strings."""

    # Override Formatter class attribute to log in UTC
    converter = time.gmtime  # type: ignore

    def format(self, record: logging.LogRecord) -> str:
        """Serializes a log record into a json string."""

        return json.dumps(
            self._record_to_dict(record),
            default=self._json_default,
            ensure_ascii=False,
        )

    def _record_to_dict(self, record: logging.LogRecord) -> dict[Any, Any]:
        """Formats a log record into a dict."""

        # Read the LogRecord's dict, ignoring unwanted keys
        result = {key: value for key, value in record.__dict__.items() if key not in UNWANTED_LOG_KEYS}

        # Msg is the value sent to the logger, we send dicts, but other librairies
        # might send str. To be consistent, we recreate a dict from the str.
        # ex: msg = {LOG_KEY: "start_receiver", "message": "Receiver started"}
        msg = result["msg"]
        if isinstance(msg, str):
            result["msg"] = {"message": msg % (result["args"] or ())}
            result.pop("args")

        elif isinstance(msg, dict):
            # Our message keys are str but other librairies might send dict
            # in this field. To be consistent, we dump the content of the field.
            if message := msg.get("message"):
                if not isinstance(message, str):
                    try:
                        result["msg"]["message"] = json.dumps(message, ensure_ascii=False)
                    except TypeError:
                        result["msg"]["message"] = str(message)

        # Compute a hash of the logging message before formatting this message
        result["msg_hash"] = _b64_hash(str(result["msg"]))
        result["record_created"] = self.formatTime(record)

        # There should be only one message in the record so that filebeat can parse it.
        if "message" in result:
            result.pop("message")

        return result

    @staticmethod
    def _json_default(obj: Any) -> str | dict | list:
        """Serializes an object into a dict, a list or a string representation of
        the object."""

        if isinstance(obj, str | dict | list):
            return obj

        if isinstance(obj, Exception):
            return [str(arg) for arg in obj.args]

        if isinstance(obj, TracebackType):
            stream = io.StringIO()
            traceback.print_tb(obj, None, stream)
            result = stream.getvalue().strip("\n")
            stream.close()

            return result

        return str(obj)


def _b64_hash(value: str) -> str:
    """Return the base64 of half the MD5 of the input data.

    This function is used to create short fingerprints in logs.
    """
    return b64encode(
        hashlib.md5(
            value.encode("utf-8"),
            usedforsecurity=False,
        ).digest()[:8]
    ).decode()
