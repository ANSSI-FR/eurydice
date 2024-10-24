import datetime
from typing import Any
from typing import Iterable
from typing import Optional

from django.db import models
from django.db.models import Q
from django.db.models import expressions
from django.db.models import functions
from django.db.models import query
from django.db.models.expressions import F
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from eurydice.common import enums
from eurydice.common import models as common_models


class Epoch(expressions.Func):
    """Django ORM database function for converting a duration to an integer
    count of seconds.
    """

    template = "EXTRACT(epoch FROM %(expressions)s)::INTEGER"
    output_field: models.IntegerField = models.IntegerField()


class ConvertSecondsToDuration(expressions.Func):
    """Django ORM database function for converting an integer count of
    seconds to a duration.
    """

    template = "make_interval(secs => %(expressions)s)"
    output_field: models.DurationField = models.DurationField()


class PythonNow(models.Value):
    """Django ORM value used for annotating the current python timestamp as opposed
    to the current database timestamp as provided by `django.db.functions.Now`
    """

    def __init__(self, value: Optional[datetime.datetime] = None, **kwargs: Any):
        super().__init__(value, **kwargs)

    def as_sql(self, *args, **kwargs):  # noqa: ANN201
        self.value = timezone.now()
        return super().as_sql(*args, **kwargs)


def _build_state_annotation() -> expressions.Case:
    """Build the annotation for computing the state when querying the
    OutgoingTransferable(s).

    The `state` is pure business logic computed in the DB.

    Returns:
        expressions.Case: the Django ORM conditions for computing
        the OutgoingTransferable's state

    """

    return expressions.Case(
        expressions.When(
            auto_user_revocations_count__gt=0,
            then=expressions.Value(enums.OutgoingTransferableState.CANCELED),
        ),
        expressions.When(
            Q(auto_error_ranges_count__gt=0) | Q(auto_revocations_count__gt=0),
            then=expressions.Value(enums.OutgoingTransferableState.ERROR),
        ),
        expressions.When(
            Q(
                submission_succeeded_at__isnull=False,
                auto_pending_ranges_count=0,
                auto_canceled_ranges_count=0,
                auto_error_ranges_count=0,
            ),
            then=expressions.Value(enums.OutgoingTransferableState.SUCCESS),
        ),
        expressions.When(
            Q(auto_ranges_count=0)
            | Q(
                auto_pending_ranges_count__gt=0,
                auto_transferred_ranges_count=0,
                auto_canceled_ranges_count=0,
                auto_error_ranges_count=0,
            ),
            then=expressions.Value(enums.OutgoingTransferableState.PENDING),
        ),
        default=expressions.Value(enums.OutgoingTransferableState.ONGOING),
        output_field=models.CharField(
            max_length=8, choices=enums.OutgoingTransferableState
        ),
    )


def _build_transfer_finished_at_annotation() -> expressions.Case:
    """Build the annotation for computing the date at which the transfer through the
    diode finished when querying the Transferable(s).

    This is done by finding the finish date for the last transferable range.
    If the transferable is still being submitted, the date is set to None.

    Returns:
        expressions.Case: the Django ORM conditions for computing the transfer finish
        date

    """
    return expressions.Case(
        expressions.When(
            submission_succeeded_at__isnull=True,
            then=None,
        ),
        expressions.When(
            models.Q(
                size=expressions.F("auto_bytes_transferred"),
                submission_succeeded_at__isnull=False,
            ),
            then="auto_last_range_finished_at",
        ),
        default=None,
        output_field=models.DateTimeField(null=True),
    )


def _build_progress_annotation() -> expressions.Case:
    """Build the annotation for computing the progress when querying the Transferable(s).

    - if a transferable has not fully been submitted, progress is None
    - if a fully submitted transferable has not yet seen any of its ranges transferred
      then it is 0
    - if a fully submitted transferable is marked as success, then it is 100
    - else it is the percentage of ranges marked TRANSFERRED

    Returns:
        expressions.Case: the Django ORM conditions for computing the transferable's
        progress

    """
    return expressions.Case(
        # handle cases when size is 0 and there is only one TransferableRange
        expressions.When(
            size=0,
            then=F("auto_transferred_ranges_count") * 100,
        ),
        # we use nullif to prevent division by zero caused by early evaluations of SQL
        # statements in specific conditions, see:
        # https://www.postgresql.org/docs/9.0/sql-expressions.html#SYNTAX-EXPRESS-EVAL
        default=expressions.F("auto_bytes_transferred")
        * 100
        / functions.NullIf(expressions.F("size"), 0),
        output_field=models.PositiveSmallIntegerField(null=True),
    )


def _build_transfer_duration_annotation() -> Epoch:
    """Build query for annotating the `transfer_duration` in seconds to the
    OutgoingTransferable.

    Returns:
        Query for the number of seconds elapsed for this transfer.

    """
    return Epoch(
        functions.Coalesce("transfer_finished_at", PythonNow())
        - expressions.F("created_at")
    )


def _build_transfer_speed_annotation() -> expressions.F:
    """Build query for annotating the `transfer_speed` in Bytes/second to the
    OutgoingTransferable.

    Returns:
        Query for the speed of this transfer.

    """
    # we use nullif to prevent division by zero caused by early evaluations of SQL
    # statements in specific conditions, see:
    # https://www.postgresql.org/docs/9.0/sql-expressions.html#SYNTAX-EXPRESS-EVAL
    return expressions.F("auto_bytes_transferred") / functions.NullIf(
        expressions.F("transfer_duration"), 0
    )


def _build_transfer_estimated_finish_date_annotation() -> expressions.Case:
    """Build query for annotating the `transfer_finish_date` to
    the OutgoingTransferable.

    Returns:
        Query for computing the transfer's finish date from its TransferableRanges

    """
    return expressions.Case(
        expressions.When(submission_succeeded_at__isnull=False, then=None),
        # we use nullif to prevent division by zero caused by early evaluations of SQL
        # statements in specific conditions, see:
        # https://www.postgresql.org/docs/9.0/sql-expressions.html#SYNTAX-EXPRESS-EVAL
        default=PythonNow()
        + ConvertSecondsToDuration(
            expressions.F("size") / functions.NullIf(expressions.F("transfer_speed"), 0)
        ),
        output_field=models.DateTimeField(null=True),
    )


class TransferableManager(models.Manager):
    def get_queryset(self) -> query.QuerySet["OutgoingTransferable"]:
        """Compute OutgoingTransferables' extra fields and annotate them to the QuerySet.

        Returns:
            The queryset annotated with the computed fields.

        """
        return (
            super()
            .get_queryset()
            .annotate(state=_build_state_annotation())
            .annotate(
                transfer_finished_at=_build_transfer_finished_at_annotation(),
            )
            .annotate(
                progress=_build_progress_annotation(),
                transfer_duration=_build_transfer_duration_annotation(),
            )
            .annotate(
                transfer_speed=_build_transfer_speed_annotation(),
            )
            .annotate(
                transfer_estimated_finish_date=(
                    _build_transfer_estimated_finish_date_annotation()
                )
            )
        )


class TransferableManagerStateOnly(models.Manager):
    def get_queryset(self) -> query.QuerySet["OutgoingTransferable"]:
        """Compute OutgoingTransferables' state and annotate it to the QuerySet.

        Returns:
            The queryset annotated with the state.

        """
        return super().get_queryset().annotate(state=_build_state_annotation())


class OutgoingTransferable(common_models.AbstractBaseModel):
    """A Transferable submitted or being submitted by a user on the origin side
    i.e. a file to transfer to the destination side.
    """

    objects = TransferableManager()

    objects_with_state_only = TransferableManagerStateOnly()

    name = common_models.TransferableNameField(
        verbose_name=_("Name"),
        help_text=_("The name of the file corresponding to the Transferable"),
        default="",
    )
    sha1 = common_models.SHA1Field(
        verbose_name=_("SHA-1"),
        help_text=_("The SHA-1 digest of the file corresponding to the Transferable"),
        null=True,
        default=None,
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
        "eurydice_origin_core.UserProfile",
        on_delete=models.RESTRICT,
        verbose_name=_("User profile"),
        help_text=_("The profile of the user owning the Transferable"),
    )
    user_provided_meta = common_models.UserProvidedMetaField(
        verbose_name=_("User provided metadata"),
        help_text=_("The metadata provided by the user on file submission"),
        default=dict,
    )
    submission_succeeded_at = models.DateTimeField(
        null=True,
        verbose_name=_("OutgoingTransferable's submission's success date"),
        help_text=_(
            "A timestamp indicating the date at which the "
            "OutgoingTransferable's submission was successful"
        ),
    )
    auto_revocations_count = models.PositiveIntegerField(
        editable=False,
        default=0,
        verbose_name=_("Associated revocations count (auto-field)"),
        help_text=_(
            "The total amount of TransferableRevocations associated to this "
            "Transferable (this field is kept up-to-date via database triggers)"
        ),
    )
    auto_user_revocations_count = models.PositiveIntegerField(
        editable=False,
        default=0,
        verbose_name=_("Associated CANCEL revocations count (auto-field)"),
        help_text=_(
            "The total amount of user cancelation TransferableRevocations associated "
            "to this Transferable (this field is kept up-to-date via database triggers)"
        ),
    )
    auto_ranges_count = models.PositiveIntegerField(
        editable=False,
        default=0,
        verbose_name=_("Associated ranges (auto-field)"),
        help_text=_(
            "The total amount of TransferableRanges associated to this Transferable "
            "(this field is kept up-to-date via database triggers)"
        ),
    )
    auto_pending_ranges_count = models.PositiveIntegerField(
        editable=False,
        default=0,
        verbose_name=_("Associated PENDING ranges (auto-field)"),
        help_text=_(
            "The total amount of TransferableRanges in PENDING state associated to "
            "this Transferable (this field is kept up-to-date via database triggers)"
        ),
    )
    auto_transferred_ranges_count = models.PositiveIntegerField(
        editable=False,
        default=0,
        verbose_name=_("Associated TRANSFERRED ranges (auto-field)"),
        help_text=_(
            "The total amount of TransferableRanges in TRANSFERRED state associated to "
            "this Transferable (this field is kept up-to-date via database triggers)"
        ),
    )
    auto_canceled_ranges_count = models.PositiveIntegerField(
        editable=False,
        default=0,
        verbose_name=_("Associated CANCELED ranges (auto-field)"),
        help_text=_(
            "The total amount of TransferableRanges in CANCELED state associated to "
            "this Transferable (this field is kept up-to-date via database triggers)"
        ),
    )
    auto_error_ranges_count = models.PositiveIntegerField(
        editable=False,
        default=0,
        verbose_name=_("Associated ERROR ranges (auto-field)"),
        help_text=_(
            "The total amount of TransferableRanges in ERROR state associated to "
            "this Transferable (this field is kept up-to-date via database triggers)"
        ),
    )
    auto_last_range_finished_at = models.DateTimeField(
        editable=False,
        null=True,
        verbose_name=_("Last associated range finish date (auto-field)"),
        help_text=_(
            "A timestamp indicating the end of the transfer of the last "
            "TransferableRange associated to this Transferable (this field is kept "
            "up-to-date via database triggers)"
        ),
    )
    auto_bytes_transferred = common_models.TransferableSizeField(
        editable=False,
        default=0,
        verbose_name=_("Amount of bytes transferred (auto-field)"),
        help_text=_(
            "The amount of this Transferable's bytes that have already been "
            "transferred (this field is kept up-to-date via database triggers)"
        ),
    )
    auto_state_updated_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name=_("Last state update date (auto-field)"),
        help_text=_(
            "A timestamp indicating the last time the state of this Transferable "
            "changed"
        ),
    )

    @property
    def submission_succeeded(self) -> bool:
        """Check if submission succeeded for this Transferable.

        Returns:
            True if the user submission for this Transferable is over,
            False otherwise

        """
        return self.submission_succeeded_at is not None

    def save(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        using: Optional[str] = None,
        update_fields: Optional[Iterable[str]] = None,
    ) -> None:
        """Hook just before Django saves, to never update auto-fields."""

        if not force_insert and update_fields is None:
            update_fields = [
                field.name
                for field in self.__class__._meta.concrete_fields
                if not field.primary_key and not field.name.startswith("auto_")
            ]

        return super().save(force_insert, force_update, using, update_fields)

    class Meta:
        db_table = "eurydice_outgoing_transferables"
        base_manager_name = "objects"
        indexes = [
            models.Index(
                fields=[
                    "-created_at",
                ]
            ),
            models.Index(
                fields=[
                    "-auto_state_updated_at",
                ]
            ),
        ]
        constraints = [
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_sha1",
                check=Q(submission_succeeded_at__isnull=True, sha1__isnull=True)
                | Q(
                    submission_succeeded_at__isnull=False,
                    sha1__isnull=False,
                    sha1__length=common_models.SHA1Field.DIGEST_SIZE_IN_BYTES,
                ),
            ),
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_bytes_received",
                check=Q(submission_succeeded_at__isnull=True)
                | Q(bytes_received=F("size")),
            ),
        ]


__all__ = ("OutgoingTransferable",)
