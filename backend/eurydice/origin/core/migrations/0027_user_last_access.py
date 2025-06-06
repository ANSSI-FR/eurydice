# Generated by Django 4.2.5 on 2023-10-12 09:07

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    dependencies = [
        ("eurydice_origin_core", "0026_alter_transferablerange_byte_offset"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="last_access",
            field=models.DateTimeField(
                blank=True,
                help_text="Unlike last_login, this field gets updated every time the user accesses the API, even when they authenticate with an API token.",
                null=True,
                verbose_name="last access",
            ),
        ),
    ]
