from typing import Any

import factory
from django.core.management import base
from django.db import transaction

from tests.destination.integration import factory as destination_factory


class Command(base.BaseCommand):  # noqa: D101
    help = "Populate the database with data resembling production"  # noqa: VNE003

    def add_arguments(self, parser: base.CommandParser) -> None:  # noqa: D102
        parser.add_argument(
            "--users",
            type=int,
            default=50,
            help="Number of users to create.",
        )
        parser.add_argument(
            "--incoming-transferables",
            type=int,
            default=300,
            help="Number of IncomingTransferables to create.",
        )
        parser.add_argument(
            "--s3-uploaded-parts",
            type=int,
            default=10000,
            help="Number of S3UploadedParts to create.",
        )

    def handle(self, *args: Any, **options: str) -> None:
        """
        Generate and populate database with data in a single query.
        """
        with transaction.atomic():
            user_profiles = destination_factory.UserProfileFactory.create_batch(
                options["users"]
            )

            incoming_transferables = (
                destination_factory.IncomingTransferableFactory.create_batch(
                    options["incoming_transferables"],
                    user_profile=factory.Iterator(user_profiles),
                )
            )

            destination_factory.S3UploadPartFactory.create_batch(
                options["s3_uploaded_parts"],
                incoming_transferable=factory.Iterator(incoming_transferables),
            )
