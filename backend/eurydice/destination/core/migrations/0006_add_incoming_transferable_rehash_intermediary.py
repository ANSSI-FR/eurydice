# Generated by Django 3.2.3 on 2021-06-03 09:45

import django.core.validators
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    dependencies = [
        ("eurydice_destination_core", "0005_update_incoming_transferable_constraints"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="incomingtransferable",
            name="eurydice_destination_core_incomingtransferable_finished_at_state",
        ),
        migrations.AddField(
            model_name="incomingtransferable",
            name="rehash_intermediary",
            field=models.BinaryField(
                default=None,
                help_text="Bytes corresponding to the internal state of the hashlib object as returned by eurydice.destination.utils.rehash.sha1_to_bytes",
                validators=[
                    django.core.validators.MaxLengthValidator(104),
                    django.core.validators.MinLengthValidator(104),
                ],
                verbose_name="Rehash intermediary",
            ),
            preserve_default=False,
        ),
        migrations.AddConstraint(
            model_name="incomingtransferable",
            constraint=models.CheckConstraint(
                check=models.Q(
                    models.Q(("finished_at__isnull", True), ("state", "ONGOING")),
                    models.Q(
                        ("finished_at__isnull", False),
                        ("state__in", {"ERROR", "SUCCESS", "EXPIRED", "REVOKED"}),
                    ),
                    _connector="OR",
                ),
                name="eurydice_destination_core_incomingtransferable_finished_at_state",
            ),
        ),
    ]
