import hashlib
from typing import Set

from django.conf import settings
from django.core import validators
from django.db import models
from django.db.models import F
from django.db.models import Q
from django.db.models import expressions
from django.db.models import functions
from django.db.models import query
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

import eurydice.common.models as common_models
import eurydice.destination.core.models as destination_models
import eurydice.destination.utils.rehash as rehash


class IncomingTransferableState(models.TextChoices):
    """
    The set of all possible values for an IncomingTransferable's state
    """

    ONGOING = "ONGOING", _("Ongoing")
    SUCCESS = "SUCCESS", _("Success")
    ERROR = "ERROR", _("Error")
    REVOKED = "REVOKED", _("Revoked")
    EXPIRED = "EXPIRED", _("Expired")
    REMOVED = "REMOVED", _("Removed")

    @classmethod
    def get_final_states(cls) -> Set["IncomingTransferableState"]:
        """List final states.

        Returns: a set containing the final states.

        """
        return {  # pytype: disable=bad-return-type
            cls.ERROR,
            cls.EXPIRED,
            cls.REVOKED,
            cls.SUCCESS,
            cls.REMOVED,
        }

    @property
    def is_final(self) -> bool:
        """Check that the state is terminal.

        Returns: True if the state is final, False otherwise.

        """
        return self in self.get_final_states()


def _build_progress_annotation() -> expressions.Case:
    """Build the annotation for computing the progress when querying the Transferable(s).

    - if a transferable has not fully been submitted, progress is None
    - else progress is the percentage of the file that was received until now

    Returns:
        Case: the Django ORM conditions for computing the transferable's progress
    """
    return expressions.Case(
        expressions.When(
            size__isnull=True,
            then=None,
        ),
        # denominator will be None if size is 0, in this case, progress must be 100
        default=functions.Coalesce(
            models.F("bytes_received") * 100 / functions.NullIf(models.F("size"), 0),
            100,
        ),
        output_field=models.PositiveSmallIntegerField(null=True),
    )


def _build_expires_at_annotation() -> expressions.Case:
    """
    Build the annotation for computing the expiration date when querying the
    Transferable.

    Returns:
        Case: the Django ORM conditions for computing the transferable's expiration date
    """
    return expressions.Case(
        expressions.When(
            models.Q(finished_at__isnull=True)
            | ~models.Q(state=IncomingTransferableState.SUCCESS),
            then=None,
        ),
        default=models.F("finished_at")
        + settings.FILE_REMOVER_EXPIRE_TRANSFERABLES_AFTER,
        output_field=models.DateTimeField(null=True),
    )


class TransferableManager(models.Manager):
    def get_queryset(self) -> query.QuerySet["IncomingTransferable"]:
        """
        Compute the progress for the queried Transferable(s) and
        annotate the queryset with it.

        Returns:
            The queryset annotated with its progress
        """

        return (
            super()
            .get_queryset()
            .annotate(
                progress=_build_progress_annotation(),
                expires_at=_build_expires_at_annotation(),
            )
        )


class IncomingTransferable(common_models.AbstractBaseModel):
    """
    A Transferable sent to the destination i.e. a file
    received or being received on the destination side.
    """

    objects = TransferableManager()

    name = common_models.TransferableNameField(
        verbose_name=_("Name"),
        help_text=_("The name of the file corresponding to the Transferable"),
    )
    sha1 = common_models.SHA1Field(
        verbose_name=_("SHA-1"),
        help_text=_("The SHA-1 digest of the file corresponding to the Transferable"),
        null=True,
        default=None,
    )
    rehash_intermediary = models.BinaryField(
        validators=[
            validators.MaxLengthValidator(rehash.SHA1_HASHLIB_BUFSIZE),
            validators.MinLengthValidator(rehash.SHA1_HASHLIB_BUFSIZE),
        ],
        verbose_name=_("Rehash intermediary"),
        help_text=_(
            "Bytes corresponding to the internal state of the hashlib object "
            "as returned by eurydice.destination.utils.rehash.sha1_to_bytes"
        ),
        default=rehash.sha1_to_bytes(hashlib.sha1(b"")),  # nosec
    )
    bytes_received = common_models.TransferableSizeField(
        verbose_name=_("Amount of bytes received"),
        help_text=_("The amount of bytes received until now for the Transferable"),
        default=0,
    )
    size = common_models.TransferableSizeField(
        verbose_name=_("Size in bytes"),
        help_text=_("The size in bytes of the file corresponding to the Transferable"),
        null=True,
        default=None,
    )

    user_profile = models.ForeignKey(
        "eurydice_destination_core.UserProfile",
        on_delete=models.RESTRICT,
        verbose_name=_("User profile"),
        help_text=_("The profile of the user owning the Transferable"),
    )
    user_provided_meta = common_models.UserProvidedMetaField(
        verbose_name=_("User provided metadata"),
        help_text=_("The metadata provided by the user on file submission"),
        default=dict,
    )
    state = models.CharField(
        max_length=7,
        choices=IncomingTransferableState.choices,
        default=IncomingTransferableState.ONGOING,
        verbose_name=_("State"),
        help_text=_("The state of the IncomingTransferable"),
    )
    finished_at = models.DateTimeField(
        null=True,
        verbose_name=_("Transfer finish date"),
        help_text=_(
            "A timestamp indicating the end of the reception of the "
            "IncomingTransferable"
        ),
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text=common_models.AbstractBaseModel.created_at.field.help_text,  # type: ignore  # noqa: E501
    )

    def _clear_multipart_data(self) -> None:
        """Delete FileUploadParts from the database for this IncomingTransferable.

        This method is meant to clear entries from the database that point to parts of
        a multipart upload for a transferable that has no data anymore.

        This method should not be called if the state of the IncomingTransferable
        is SUCCESS.
        """
        destination_models.FileUploadPart.objects.filter(
            incoming_transferable=self
        ).delete()

    def _mark_as_finished(
        self,
        state: IncomingTransferableState,
        save: bool = True,
        remove_file_uploaded_parts: bool = False,
    ) -> None:
        """Mark the IncomingTransferable as `state` and set its finish date to now.

        Args:
            state: the IncomingTransferableState the IncomingTransferable must be
                set to.
            save: boolean indicating whether changed fields should be saved or not.
            remove_file_uploaded_parts: boolean indicating whether associated
                FileUploadParts should be deleted or not.

        """
        self.state = state
        self.finished_at = timezone.now()

        if save:
            self.save(update_fields=["state", "finished_at"])
        if remove_file_uploaded_parts:
            self._clear_multipart_data()

    def mark_as_error(self, save: bool = True) -> None:
        """Mark the IncomingTransferable as ERROR and set its finish date to now.

        Args:
            save: boolean indicating whether changes should be saved to database
                or simply edited in the ORM instance.
        """
        self._mark_as_finished(  # pytype: disable=wrong-arg-types
            IncomingTransferableState.ERROR,
            save,
            remove_file_uploaded_parts=True,
        )

    def mark_as_revoked(self, save: bool = True) -> None:
        """Mark the IncomingTransferable as REVOKED and set its finish date to now.

        Args:
            save: boolean indicating whether changes should be saved to database
                or simply edited in the ORM instance.
        """
        self._mark_as_finished(  # pytype: disable=wrong-arg-types
            IncomingTransferableState.REVOKED,
            save,
            remove_file_uploaded_parts=True,
        )

    def mark_as_success(self, save: bool = True) -> None:
        """Mark the IncomingTransferable as SUCCESS and set its finish date to now.

        Args:
            save: boolean indicating whether changes should be saved to database
                or simply edited in the ORM instance.
        """
        self._mark_as_finished(  # pytype: disable=wrong-arg-types
            IncomingTransferableState.SUCCESS,
            save,
        )

    def mark_as_expired(self, save: bool = True) -> None:
        """Mark the IncomingTransferable as EXPIRED.

        Args:
            save: boolean indicating whether changes should be saved to database
                or simply edited in the ORM instance.
        """
        self.state = IncomingTransferableState.EXPIRED

        if save:
            self.save(update_fields=["state"])
        self._clear_multipart_data()

    def mark_as_removed(self, save: bool = True) -> None:
        """Mark the IncomingTransferable as REMOVED.

        Args:
            save: boolean indicating whether changes should be saved to database
                or simply edited in the ORM instance.
        """
        self.state = IncomingTransferableState.REMOVED

        if save:
            self.save(update_fields=["state"])
        self._clear_multipart_data()

    class Meta:
        db_table = "eurydice_incoming_transferables"
        indexes = [
            models.Index(
                fields=[
                    "-created_at",
                ]
            ),
            models.Index(fields=["created_at", "state"], name="created_at_state_idx"),
        ]
        constraints = [
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_finished_at_state",
                check=(
                    Q(
                        finished_at__isnull=True,
                        state=IncomingTransferableState.ONGOING,
                    )
                    | Q(
                        finished_at__isnull=False,
                        state__in=IncomingTransferableState.get_final_states(),
                    )
                ),
            ),
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_sha1",
                check=~Q(state=IncomingTransferableState.SUCCESS)
                | Q(
                    sha1__isnull=False,
                    sha1__length=common_models.SHA1Field.DIGEST_SIZE_IN_BYTES,
                ),
            ),
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_rehash_intermediary",
                check=Q(rehash_intermediary__length=rehash.SHA1_HASHLIB_BUFSIZE),
            ),
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_bytes_received",
                check=~Q(state=IncomingTransferableState.SUCCESS)
                | Q(bytes_received=F("size")),
            ),
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_finished_at_created_at",
                check=Q(finished_at__gte=F("created_at")),
            ),
        ]


__all__ = ("IncomingTransferable", "IncomingTransferableState")
