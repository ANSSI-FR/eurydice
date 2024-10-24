from django.db import models
from django.utils.translation import gettext_lazy as _


class TransferableRangeTransferState(models.TextChoices):
    """The set of all possible transfer states for a TransferableRange."""

    PENDING = "PENDING", _("Pending")
    TRANSFERRED = "TRANSFERRED", _("Transferred")
    CANCELED = "CANCELED", _("Canceled")
    ERROR = "ERROR", _("Error")


class TransferableRevocationTransferState(models.TextChoices):
    """The set of all possible transfer states for a TransferableRevocation."""

    PENDING = "PENDING", _("Pending")
    TRANSFERRED = "TRANSFERRED", _("Transferred")
    ERROR = "ERROR", _("Error")


__all__ = ("TransferableRangeTransferState", "TransferableRevocationTransferState")
