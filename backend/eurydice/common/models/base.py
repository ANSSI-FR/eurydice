import uuid
from datetime import datetime
from typing import Optional

from django.db import models
from django.utils.translation import gettext_lazy as _


class AbstractBaseModel(models.Model):
    """
    Model using an UUID4 as primary key and
    with automatic created_at field.
    """

    id = models.UUIDField(  # noqa: VNE003
        primary_key=True, default=uuid.uuid4, editable=False
    )

    created_at = models.DateTimeField(auto_now_add=True, help_text=_("Creation date"))

    class Meta:
        abstract = True
        ordering = ("-created_at",)


class SingletonModel(models.Model):
    """Model which can have only one instance persisted in the database."""

    id = models.UUIDField(  # noqa: VNE003
        primary_key=True, default=uuid.uuid4, editable=False
    )
    _singleton = models.BooleanField(default=True, editable=False, unique=True)

    class Meta:
        abstract = True


class TimestampSingleton(SingletonModel):
    """Singleton holding a timestamp."""

    timestamp = models.DateTimeField(auto_now=True)

    @classmethod
    def update(cls) -> None:
        """Update timestamp to current time."""
        cls.objects.update_or_create()

    @classmethod
    def get_timestamp(cls) -> Optional[datetime]:
        """Get the timestamp of the last received packet.

        Returns None if no packet has ever been received.
        """
        try:
            return cls.objects.get().timestamp
        except cls.DoesNotExist:
            return None

    class Meta:
        abstract = True


__all__ = ("AbstractBaseModel", "SingletonModel", "TimestampSingleton")
