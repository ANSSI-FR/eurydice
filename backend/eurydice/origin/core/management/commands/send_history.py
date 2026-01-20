import logging
import time
from typing import Any

import humanfriendly
from django.conf import settings
from django.core.management import base

import eurydice.common.protocol as protocol
import eurydice.origin.sender.packet_generator.fillers as fillers
import eurydice.origin.sender.utils as sender_utils
from eurydice.common.logging.logger import LOG_KEY, logger
from eurydice.origin.sender import packet_sender


def _print_and_log(message: str, level: int = logging.INFO) -> None:
    print(message)
    if level == logging.INFO:
        logger.info({LOG_KEY: "send_history_command", "message": message})
    else:
        logger.debug({LOG_KEY: "send_history_command", "message": message})


class Command(base.BaseCommand):
    help = "Force-send a history of given duration. Bypasses Maintenance mode. Only sends history, does not send Transferable ranges or revocations."  # noqa: E501

    def add_arguments(self, parser: base.CommandParser) -> None:  # noqa: D102
        parser.add_argument(
            "--duration",
            type=str,
            default="7d",
            help="Duration of history, in humanfriendly time format (15min, 6h, 7d...)",
        )

    def handle(self, *args: Any, **options: str) -> None:
        """
        Sends an OTWPacket using only the History filler.
        """
        settings.TRANSFERABLE_HISTORY_DURATION = humanfriendly.parse_timespan(options["duration"])

        sender_utils.check_configuration()

        _print_and_log("Preparing sender...", logging.DEBUG)
        with packet_sender.PacketSender() as sender:
            _print_and_log("Ready to send OnTheWirePackets")

            _print_and_log("Generating history packet...", logging.DEBUG)
            start = time.perf_counter()

            # manually use OngoingHistoryFiller to bypass maintenance mode
            packet = protocol.OnTheWirePacket()  # type: ignore
            fillers.OngoingHistoryFiller().fill(packet)

            end = time.perf_counter()
            elapsed_time = end - start
            _print_and_log(f"Generated packet in {elapsed_time} seconds.")

            _print_and_log("Sending packet...", logging.DEBUG)
            start = time.perf_counter()

            sender.send(packet)

            end = time.perf_counter()
            elapsed_time = end - start
            _print_and_log(f"Packet sent in {elapsed_time} seconds.")

        _print_and_log("Done.")
