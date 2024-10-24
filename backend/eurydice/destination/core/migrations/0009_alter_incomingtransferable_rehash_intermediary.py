# Generated by Django 3.2.3 on 2021-06-23 08:49

import hashlib

import django.core.validators
from django.db import migrations
from django.db import models

from eurydice.destination.utils import rehash


class Migration(migrations.Migration):
    dependencies = [
        (
            "eurydice_destination_core",
            "0008_remove_incomingtransferable_s3_nb_uploaded_parts",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="incomingtransferable",
            name="rehash_intermediary",
            field=models.BinaryField(
                default=rehash.sha1_to_bytes(hashlib.sha1(b"")),  # nosec
                help_text="Bytes corresponding to the internal state of the hashlib object as returned by eurydice.destination.utils.rehash.sha1_to_bytes",
                validators=[
                    django.core.validators.MaxLengthValidator(104),
                    django.core.validators.MinLengthValidator(104),
                ],
                verbose_name="Rehash intermediary",
            ),
        ),
    ]