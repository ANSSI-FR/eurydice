# Generated by Django 3.2.2 on 2021-05-19 15:14

import django.db.models.deletion
from django.conf import settings
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    dependencies = [
        ("eurydice_destination_core", "0001_initial"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="userprofile",
            name="eurydice_destination_core_userprofile_user_associated_user_profile_id",
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="associated_user_profile_id",
            field=models.UUIDField(
                help_text="The UUID of the user profile on the origin side that is associated with the user profile on this side",
                unique=True,
                verbose_name="Associated user profile ID",
            ),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="user",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="user_profile",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]