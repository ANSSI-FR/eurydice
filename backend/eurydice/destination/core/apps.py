from django import apps
from django.db import models
from django.db.models import functions


class CoreConfig(apps.AppConfig):
    name = "eurydice.destination.core"
    label = "eurydice_destination_core"
    verbose_name = "Eurydice"

    def ready(self) -> None:
        # Register lookups
        models.CharField.register_lookup(functions.Length)
        models.BinaryField.register_lookup(functions.Length)
