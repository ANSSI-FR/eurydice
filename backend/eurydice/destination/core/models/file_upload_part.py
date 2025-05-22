from django.core import validators
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

import eurydice.common.models as common_models


class FileUploadPart(common_models.AbstractBaseModel):
    """Model representing a part in an file multipart upload."""

    part_number = models.PositiveIntegerField(
        validators=[
            validators.MinValueValidator(1),
        ],
        verbose_name=_("File multipart upload part number"),
        help_text=_("The index of this part within the multipart upload."),
    )
    incoming_transferable = models.ForeignKey(
        "eurydice_destination_core.IncomingTransferable",
        on_delete=models.RESTRICT,
        related_name="file_upload_parts",
        verbose_name=_("Incoming Transferable"),
        help_text=_("The profile of the user owning the Transferable"),
    )

    class Meta:
        db_table = "eurydice_file_upload_part"
        constraints = [
            models.UniqueConstraint(
                name="%(app_label)s_%(class)s_incoming_transferable_part_number",
                fields=["incoming_transferable", "part_number"],
            ),
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_part_number",
                check=Q(part_number__gte=1),
            ),
        ]
