from typing import Any

import factory
from django.core.management import base
from django.db import transaction

from tests.origin.integration import factory as origin_factory


class Command(base.BaseCommand):
    help = "Populate the database with data resembling production"

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
            user_profiles = origin_factory.UserProfileFactory.create_batch(options["users"])  # type: ignore[arg-type]

            outgoing_transferables = origin_factory.OutgoingTransferableFactory.create_batch(
                options["outgoing_transferables"],  # type: ignore[arg-type]
                user_profile=factory.Iterator(user_profiles),  # type: ignore[attr-defined, no-untyped-call]
            )

            origin_factory.TransferableRangeFactory.create_batch(
                options["transferable_ranges"],  # type: ignore[arg-type]
                outgoing_transferable=factory.Iterator(outgoing_transferables),  # type: ignore[attr-defined, no-untyped-call]
            )
