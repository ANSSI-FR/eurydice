from django.db import models


class MonitoringPermissions(models.Model):
    """An unmanaged model that holds monitoring permissions users possess."""

    class Meta:
        managed = False  # no associated database table
        default_permissions = ()  # disable default permissions ("add", "change"...)

        permissions = (("view_rolling_metrics", "Can view rolling metrics"),)


__all__ = ("MonitoringPermissions",)
