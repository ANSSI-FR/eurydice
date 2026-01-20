from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

import eurydice.common.models as common_models


class User(common_models.AbstractUser):
    """A user on the destination side."""


class UserProfile(common_models.AbstractBaseModel):
    """User profile metadata."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        related_name="user_profile",
    )
    associated_user_profile_id = models.UUIDField(
        unique=True,
        verbose_name=_("Associated user profile ID"),
        help_text=_(
            "The UUID of the user profile on the origin side that is associated with the user profile on this side"
        ),
    )

    class Meta:
        db_table = "eurydice_user_profiles"


__all__ = ("User", "UserProfile")
