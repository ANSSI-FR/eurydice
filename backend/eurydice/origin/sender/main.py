import datetime
import time

from django.conf import settings
from django.db import connections
from django.utils import timezone

import eurydice.origin.sender.utils as sender_utils
from eurydice.common import protocol
from eurydice.common.logging.logger import LOG_KEY, logger
from eurydice.common.utils import signals
from eurydice.origin.core.models import LastPacketSentAt
from eurydice.origin.sender import packet_generator, packet_sender


def _log_packet_stats(packet: protocol.OnTheWirePacket) -> None:
    """
    Log the given packets' statistics

    Args:
        packet: packet to log stats about
    """
    if packet.is_empty():
        logger.info({LOG_KEY: "packet_stats", "message": "sending heartbeat"})
    else:
        logger.info({LOG_KEY: "packet_stats", "message": f"Sending {packet}"})


def _heartbeat_should_be_sent(last_packet_sent_at: datetime.datetime | None) -> bool:
    """
    Determine if a heartbeat should be send based on the previous packet's send date

    Args:
        last_packet_sent_at: datetime at which last packet was sent

    Returns:
        True if heartbeat should be sent, False otherwise
    """
    # Always send a heartbeat upon starting up
    if last_packet_sent_at is None:
        return True
    return timezone.now() >= last_packet_sent_at + datetime.timedelta(seconds=settings.HEARTBEAT_SEND_EVERY)


def _loop() -> None:
    """
    Loop indefinitely until interrupted, sending packets as they become available
    along with heartbeats when no packets are sent.
    """

    sender_utils.check_configuration()

    generator = packet_generator.OnTheWirePacketGenerator()
    keep_running = signals.BooleanCondition()

    with packet_sender.PacketSender() as sender:
        logger.info({LOG_KEY: "sender_ready", "message": "Ready to send OnTheWirePackets"})

        while keep_running:
            packet = generator.generate_next_packet()

            if not packet.is_empty() or _heartbeat_should_be_sent(sender.last_packet_sent_at):
                sender.send(packet)
                LastPacketSentAt.update()
                _log_packet_stats(packet)
            else:
                time.sleep(settings.SENDER_POLL_DATABASE_EVERY)


def run() -> None:  # pragma: no cover
    """Entrypoint for the sender."""
    try:
        _loop()
    finally:
        connections.close_all()


__all__ = ("run",)
