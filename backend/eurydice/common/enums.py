"""Enums used both on the origin and destination sides."""

from typing import Set

from django.db import models
from django.utils.translation import gettext_lazy as _


class OutgoingTransferableState(models.TextChoices):
    """The set of all possible "global" states for an OutgoingTransferable."""

    PENDING = "PENDING", _("Pending")
    ONGOING = "ONGOING", _("Ongoing")
    ERROR = "ERROR", _("Error")
    CANCELED = "CANCELED", _("Canceled")
    SUCCESS = "SUCCESS", _("Success")

    @classmethod
    def get_final_states(cls) -> Set["OutgoingTransferableState"]:
        """List final states.

        Returns: a set containing the final states.

        """
        return {cls.ERROR, cls.CANCELED, cls.SUCCESS}

    @property
    def is_final(self) -> bool:
        """Check that the state is terminal.

        Returns: True if the state is final, False otherwise.

        """
        return self in self.get_final_states()


class TransferableRevocationReason(models.TextChoices):
    """The set of all possible revocation reasons for an a TransferableRevocation."""

    USER_CANCELED = "USER_CANCELED", _("Canceled by the user")
    UPLOAD_SIZE_MISMATCH = (
        "UPLOAD_SIZE_MISMATCH",
        _("The size of the uploaded Transferable did not match the size given in the Content-Length header."),
    )
    OBJECT_STORAGE_FULL = "OBJECT_STORAGE_FULL", _("No more space on API object storage")
    UNEXPECTED_EXCEPTION = "UNEXPECTED_EXCEPTION", _("Unexpected error occurred while handling Transferable")
    UPLOAD_INTERRUPTION = "UPLOAD_INTERRUPTION", _("Multipart upload was interrupted")


__all__ = (
    "OutgoingTransferableState",
    "TransferableRevocationReason",
)
