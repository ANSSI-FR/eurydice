# Generated by Django 3.2.4 on 2021-06-30 09:46

import django.utils.timezone
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    dependencies = [
        (
            "eurydice_destination_core",
            "0009_alter_incomingtransferable_rehash_intermediary",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="incomingtransferable",
            name="created_at",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
