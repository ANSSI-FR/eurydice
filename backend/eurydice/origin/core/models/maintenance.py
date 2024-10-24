from django.db import models
from django.utils.translation import gettext_lazy as _

from eurydice.common import models as common_models


class Maintenance(common_models.SingletonModel):
    """Singleton holding whether the app is in maintenance mode."""

    maintenance = models.BooleanField(
        _("Whether the app is currently in maintenance mode.")
    )

    class Meta:
        db_table = "eurydice_maintenance"

    @classmethod
    def is_maintenance(cls) -> bool:
        """Returns whether the app is currently in maintenance mode."""
        try:
            return cls.objects.get().maintenance
        except cls.DoesNotExist:
            return False
