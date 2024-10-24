import uuid

import django.contrib.auth.models
from django.db import models
from django.utils.translation import gettext_lazy as _


class AbstractUser(django.contrib.auth.models.AbstractUser):
    """A custom abstract user model using an UUID4 as primary key."""

    id = models.UUIDField(  # noqa: VNE003
        primary_key=True, default=uuid.uuid4, editable=False
    )

    last_access = models.DateTimeField(
        _("last access"),
        help_text=(
            "Unlike last_login, this field gets updated every time the "
            "user accesses the API, even when they authenticate with an API token."
        ),
        blank=True,
        null=True,
    )

    class Meta:
        abstract = True


__all__ = ("AbstractUser",)
