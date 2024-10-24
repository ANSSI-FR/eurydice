from django import apps


class PermissionsConfig(apps.AppConfig):
    name = "eurydice.common.permissions"
    label = "eurydice_common_permissions"
    default_auto_field = "django.db.models.AutoField"
