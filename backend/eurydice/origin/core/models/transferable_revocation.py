from django.db import models
from django.db.models.expressions import F
from django.utils.translation import gettext_lazy as _

from eurydice.common import enums
from eurydice.common import models as common_models
from eurydice.origin.core import enums as origin_enums
from eurydice.origin.core import models as origin_models


class TransferableRevocationQuerySet(models.QuerySet):
    def list_pending(self) -> models.QuerySet:
        """List `PENDING` TransferableRevocations ordered by date.

        Returns:
            A QuerySet for the `PENDING` TransferableRevocations.

        """
        return self.filter(
            transfer_state=origin_enums.TransferableRevocationTransferState.PENDING,
        ).order_by("created_at")


class TransferableRevocation(common_models.AbstractBaseModel):
    """The revocation for a Transferable.

    Stored in the DB to be transferred through the diode in order
    to revoke the Transferable on the destination API.

    Attributes:
        outgoing_transferable: The transferable to be revoked
        reason: The reason for the revocation
        transfer_state: The state of the Revocation's transfer through the diode

    """

    objects = TransferableRevocationQuerySet.as_manager()

    outgoing_transferable = models.OneToOneField(
        origin_models.OutgoingTransferable,
        on_delete=models.CASCADE,
        related_name="revocation",
    )
    reason = models.CharField(
        max_length=20,
        choices=enums.TransferableRevocationReason.choices,
        verbose_name=_("Revocation reason"),
        help_text=_("The reason for the OutgoingTransferable's revocation"),
    )
    transfer_state = models.CharField(
        max_length=11,
        choices=origin_enums.TransferableRevocationTransferState.choices,
        default=origin_enums.TransferableRevocationTransferState.PENDING,
        verbose_name=_("State of the Revocation"),
        help_text=_("The OutgoingTransferable's revocation state"),
    )

    class Meta:
        db_table = "eurydice_transferable_revocations"
        indexes = [
            models.Index(
                F("outgoing_transferable_id"),
                name="eurydice_revocations_fgn_key",
            )
        ]


__all__ = ("TransferableRevocation",)
