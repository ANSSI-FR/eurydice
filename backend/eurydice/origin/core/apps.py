from django import apps
from django.conf import settings
from django.db import models
from django.db.models import functions


class CoreConfig(apps.AppConfig):
    name = "eurydice.origin.core"
    label = "eurydice_origin_core"
    verbose_name = "Eurydice"

    def ready(self) -> None:
        if settings.MINIO_ENABLED:
            from eurydice.common.utils import s3 as s3_utils

            s3_utils.create_bucket_if_does_not_exist()

        # Import django DB signals to register them
        import eurydice.origin.core.signals  # noqa: F401

        # Register lookups
        models.CharField.register_lookup(functions.Length)
        models.BinaryField.register_lookup(functions.Length)
