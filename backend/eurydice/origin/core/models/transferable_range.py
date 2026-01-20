from django.conf import settings
from django.core import validators
from django.db import models
from django.db.models import Q
from django.db.models.expressions import F
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

import eurydice.common.models as common_models
from eurydice.origin.core import enums


class TransferableRange(common_models.AbstractBaseModel):
    """A fragment of an OutgoingTransferable i.e. a chunk of a file submitted by
    a user.
    """

    byte_offset: models.PositiveBigIntegerField = models.PositiveBigIntegerField(
        validators=(validators.MaxValueValidator(settings.TRANSFERABLE_MAX_SIZE),),
        verbose_name=_("Byte offset"),
        help_text=_("The start position of this range in the associated Transferable"),
    )
    size: models.PositiveIntegerField = models.PositiveIntegerField(
        validators=(validators.MaxValueValidator(settings.TRANSFERABLE_RANGE_SIZE),),
        verbose_name=_("Size in bytes"),
        help_text=_("The size in bytes of this TransferableRange"),
    )
    transfer_state: models.CharField = models.CharField(
        max_length=11,
        choices=enums.TransferableRangeTransferState.choices,
        default=enums.TransferableRangeTransferState.PENDING,
        verbose_name=_("Transfer state"),
        help_text=_("The state of the transfer for this OutgoingTransferable"),
    )
    finished_at: models.DateTimeField = models.DateTimeField(
        null=True,
        verbose_name=_("Transfer finish date"),
        help_text=_("A timestamp indicating the end of the transfer of the Transferable"),
    )
    outgoing_transferable = models.ForeignKey(
        "eurydice_origin_core.OutgoingTransferable",
        on_delete=models.CASCADE,
        related_name="transferable_ranges",
    )

    @cached_property
    def is_last(self) -> bool:
        """Assert this TransferableRange is the last of the Transferable.

        Returns:
            bool:   True if this TransferableRange is the last for the associated
                    Transferable, False otherwise
        """
        if not self.outgoing_transferable.submission_succeeded:
            return False

        if self.outgoing_transferable.size is not None and self.outgoing_transferable.size == self.size:
            return True

        return (
            type(self)  # type: ignore[union-attr]
            ._default_manager.filter(outgoing_transferable__id=self.outgoing_transferable.id)
            .order_by("byte_offset")
            .only("id")
            .last()
            .id
            == self.id
        )

    def _mark_as_finished(self, transfer_state: enums.TransferableRangeTransferState, save: bool) -> None:
        """
        Mark the TransferableRange as `transfer_state` and set its finish date
        to now.

        Args:
            transfer_state: the TransferState the TransferableRange must be set to.
            save: whether changed fields should be saved or not.

        """
        self.transfer_state = transfer_state
        self.finished_at = timezone.now()

        if save:
            self.save(update_fields=["transfer_state", "finished_at"])

    def mark_as_transferred(self, save: bool = True) -> None:
        """
        Mark the current TransferableRange as TRANSFERRED in the DB and set
        its finish date to now.
        """
        self._mark_as_finished(enums.TransferableRangeTransferState.TRANSFERRED, save)

    def mark_as_canceled(self, save: bool = True) -> None:
        """
        Mark the current TransferableRange as REVOKED in the DB and set
        its finish date to now.
        """
        self._mark_as_finished(enums.TransferableRangeTransferState.CANCELED, save)

    def mark_as_error(self, save: bool = True) -> None:
        """
        Mark the current TransferableRange as ERROR in the DB and set
        its finish date to now.
        """
        self._mark_as_finished(enums.TransferableRangeTransferState.ERROR, save)

    class Meta:
        db_table = "eurydice_transferable_ranges"
        constraints = [
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_finished_at_transfer_state",
                check=(
                    Q(
                        finished_at__isnull=True,
                        transfer_state=enums.TransferableRangeTransferState.PENDING,
                    )
                    | Q(
                        finished_at__isnull=False,
                        transfer_state__in=(
                            enums.TransferableRangeTransferState.ERROR,
                            enums.TransferableRangeTransferState.TRANSFERRED,
                            enums.TransferableRangeTransferState.CANCELED,
                        ),
                    )
                ),
            ),
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_finished_at_created_at",
                check=Q(finished_at__gte=F("created_at")),
            ),
        ]
        indexes = [
            models.Index(
                F("outgoing_transferable_id"),
                name="eurydice_pending_ranges",
                condition=Q(transfer_state="PENDING"),
            ),
            models.Index(
                F("outgoing_transferable_id"),
                name="eurydice_error_ranges",
                condition=Q(transfer_state="ERROR"),
            ),
        ]


__all__ = ("TransferableRange",)
