# Generated by Django 4.2.2 on 2023-07-28 16:10

import uuid

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    dependencies = [
        (
            "eurydice_destination_core",
            "0020_user_last_access",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="LastPacketReceivedAt",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "_singleton",
                    models.BooleanField(default=True, editable=False, unique=True),
                ),
                ("timestamp", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "eurydice_last_packet_received_at",
            },
        ),
    ]
