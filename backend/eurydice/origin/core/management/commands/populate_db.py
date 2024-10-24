from typing import Any

import factory
from django.core.management import base
from django.db import transaction

from tests.origin.integration import factory as origin_factory


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
            "--outgoing-transferables",
            type=int,
            default=300,
            help="Number of OutgoingTransferables to create.",
        )
        parser.add_argument(
            "--transferable-ranges",
            type=int,
            default=50000,
            help="Number of TransferableRanges to create.",
        )

    def handle(self, *args: Any, **options: str) -> None:
        """
        Generate and populate database with data in a single query.
        """
        with transaction.atomic():
            user_profiles = origin_factory.UserProfileFactory.create_batch(
                options["users"]
            )

            outgoing_transferables = (
                origin_factory.OutgoingTransferableFactory.create_batch(
                    options["outgoing_transferables"],
                    user_profile=factory.Iterator(user_profiles),
                )
            )

            origin_factory.TransferableRangeFactory.create_batch(
                options["transferable_ranges"],
                outgoing_transferable=factory.Iterator(outgoing_transferables),
            )
