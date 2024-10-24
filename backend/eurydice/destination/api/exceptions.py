from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions
from rest_framework import status


class AlreadyAssociatedError(exceptions.APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = _(
        "The user is already associated with a user from the origin side."
    )
    # mypy does not recognize qualname
    # https://github.com/python/mypy/issues/6473
    default_code = __qualname__


class TransferableErroredError(exceptions.APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = _(
        "An error was encountered while processing the Transferable"
        " it is not available for download."
    )
    # mypy does not recognize qualname
    # https://github.com/python/mypy/issues/6473
    default_code = __qualname__


class TransferableExpiredError(exceptions.APIException):
    status_code = status.HTTP_410_GONE
    default_detail = _(
        "The transferable has expired and its data was removed to limit disk usage."
    )
    # mypy does not recognize qualname
    # https://github.com/python/mypy/issues/6473
    default_code = __qualname__


class TransferableOngoingError(exceptions.APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = _(
        "The transferable is still ongoing and was not yet successfully received."
    )
    # mypy does not recognize qualname
    # https://github.com/python/mypy/issues/6473
    default_code = __qualname__


class TransferableRemovedError(exceptions.APIException):
    status_code = status.HTTP_410_GONE
    default_detail = _("The data of the transferable has been removed by the user.")
    # mypy does not recognize qualname
    # https://github.com/python/mypy/issues/6473
    default_code = __qualname__


class TransferableRevokedError(exceptions.APIException):
    status_code = status.HTTP_410_GONE
    default_detail = _(
        "The transferable has been revoked and "
        "its data was removed to limit disk usage."
    )
    # mypy does not recognize qualname
    # https://github.com/python/mypy/issues/6473
    default_code = __qualname__


class UnsuccessfulTransferableError(exceptions.APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = _(
        "The transferable was not successfully received and cannot be deleted."
    )
    # mypy does not recognize qualname
    # https://github.com/python/mypy/issues/6473
    default_code = __qualname__


__all__ = (
    "AlreadyAssociatedError",
    "TransferableErroredError",
    "TransferableExpiredError",
    "TransferableOngoingError",
    "TransferableRemovedError",
    "TransferableRevokedError",
    "UnsuccessfulTransferableError",
)
