# Generated by Django 3.2.5 on 2021-07-30 07:19

import django.core.validators
from django.db import migrations

import eurydice.common.models.fields


class Migration(migrations.Migration):
    dependencies = [
        ("eurydice_destination_core", "0010_alter_incomingtransferable_created_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="incomingtransferable",
            name="bytes_received",
            field=eurydice.common.models.fields.TransferableSizeField(
                default=0,
                help_text="The amount of bytes received until now for the Transferable",
                validators=[django.core.validators.MaxValueValidator(5497558138880)],
                verbose_name="Amount of bytes received",
            ),
        ),
        migrations.AlterField(
            model_name="incomingtransferable",
            name="size",
            field=eurydice.common.models.fields.TransferableSizeField(
                default=None,
                help_text="The size in bytes of the file corresponding to the Transferable",
                null=True,
                validators=[django.core.validators.MaxValueValidator(5497558138880)],
                verbose_name="Size in bytes",
            ),
        ),
    ]