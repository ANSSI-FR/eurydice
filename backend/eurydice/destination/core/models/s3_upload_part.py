from django.core import validators
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

import eurydice.common.models as common_models

_S3_PART_ETAG_LENGTH = 16  # bytes


class S3UploadPart(common_models.AbstractBaseModel):
    """Model representing a part in an S3 multipart upload."""

    etag = models.BinaryField(
        max_length=_S3_PART_ETAG_LENGTH,
        validators=[
            validators.MinLengthValidator(_S3_PART_ETAG_LENGTH),
        ],
        verbose_name=_("S3 multipart upload part ETag"),
        help_text=_(
            "Bytes corresponding to the MD5 sum for the upload part. "
            "Note that S3 multipart upload parts' ETags should always be an MD5 sum. "
            "https://docs.aws.amazon.com/AmazonS3/latest/API/API_Object.html"
        ),
    )
    part_number = models.PositiveIntegerField(
        validators=[
            validators.MinValueValidator(1),
        ],
        verbose_name=_("S3 multipart upload part number"),
        help_text=_("The index of this part within the multipart upload."),
    )
    incoming_transferable = models.ForeignKey(
        "eurydice_destination_core.IncomingTransferable",
        on_delete=models.RESTRICT,
        related_name="s3_upload_parts",
        verbose_name=_("Incoming Transferable"),
        help_text=_("The profile of the user owning the Transferable"),
    )

    class Meta:
        db_table = "eurydice_s3_upload_part"
        constraints = [
            models.UniqueConstraint(
                name="%(app_label)s_%(class)s_incoming_transferable_part_number",
                fields=["incoming_transferable", "part_number"],
            ),
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_etag",
                check=Q(etag__length=_S3_PART_ETAG_LENGTH),
            ),
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_part_number",
                check=Q(part_number__gte=1),
            ),
        ]
