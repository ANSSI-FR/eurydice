"""This module declares Django database signals"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from eurydice.origin.core import models


@receiver(post_save, sender=models.User)
def create_user_profile(instance: models.User, created: bool, *args, **kwargs) -> None:
    """Create a UserProfile for the created user

    Args:
        instance (models.User): the created user instance

    """
    if created:
        try:
            instance.user_profile  # type: ignore
        except models.UserProfile.DoesNotExist:
            models.UserProfile.objects.create(user=instance)
