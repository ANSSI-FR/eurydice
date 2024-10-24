from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

import eurydice.common.models as common_models


class User(common_models.AbstractUser):
    """A user on the origin side."""


class UserProfile(common_models.AbstractBaseModel):
    """User profile metadata."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_profile"
    )
    priority = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_("Priority"),
        help_text=_("The priority level of the related user for transmitting files"),
    )

    class Meta:
        db_table = "eurydice_user_profiles"


__all__ = ("User", "UserProfile")
