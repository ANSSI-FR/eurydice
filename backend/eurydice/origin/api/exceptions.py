from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, status


class MissingContentTypeError(exceptions.APIException):
    """Exception raised when the Content-Type header is missing when it was expected."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("Content-Type header is missing")
    # mypy does not recognize qualname
    # https://github.com/python/mypy/issues/6473
    default_code = __qualname__


class InconsistentContentLengthError(exceptions.APIException):
    """Exception raised when the Content-Length does not match the
    number of bytes read from the request's body.

    Args:
        read: the number of bytes actually read.
        expected: the expected number of bytes.

    """

    def __init__(self, read: int, expected: int):
        super().__init__(
            detail=_(
                "Content-Length header does not match the size of the request's body. "
                f"Read {read} bytes, expected {expected}."
            )
        )

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("Content-Length header does not match the size of the request's body.")
    # mypy does not recognize qualname
    # https://github.com/python/mypy/issues/6473
    default_code = __qualname__


class InvalidContentLengthError(exceptions.APIException):
    """Exception raised when the Content-Length header has an invalid value"""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("Invalid value for Content-Length header")
    # mypy does not recognize qualname
    # https://github.com/python/mypy/issues/6473
    default_code = __qualname__


class RequestEntityTooLargeError(exceptions.APIException):
    """Exception raised when the Content-Length exceeds the configured
    maximum Transferable size.
    """

    status_code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
    default_detail = _(
        "The uploaded Transferable is too large or the Content-Length header indicates "
        "that the Transferable in the body will be too large to be saved."
    )
    # mypy does not recognize qualname
    # https://github.com/python/mypy/issues/6473
    default_code = __qualname__


class TransferableNotSuccessfullySubmittedError(exceptions.APIException):
    """Exception raised when a transferable has not been successfully submitted."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "The uploaded transferable has not been successfully submitted."
    # mypy does not recognize qualname
    # https://github.com/python/mypy/issues/6473
    default_code = __qualname__


__all__ = (
    "MissingContentTypeError",
    "InconsistentContentLengthError",
    "InvalidContentLengthError",
    "RequestEntityTooLargeError",
    "TransferableNotSuccessfullySubmittedError",
)
