import datetime

from django.conf import settings
from django.db import connections
from django.utils import timezone

from eurydice.common import protocol
from eurydice.common.logging.logger import LOG_KEY, logger
from eurydice.common.utils import signals
from eurydice.destination.core.models import LastPacketReceivedAt
from eurydice.destination.receiver import packet_handler, packet_receiver


class _PacketLogger:
    """Log received and missed packets."""

    def __init__(self) -> None:
        self._last_log_at: datetime.datetime = timezone.now()

    def log_received(self, packet: protocol.OnTheWirePacket) -> None:
        """Log the reception of a packet."""
        if packet.is_empty():
            logger.info({LOG_KEY: "heartbeat_received"})
        else:
            logger.info(
                {
                    LOG_KEY: "heartbeat_received",
                    "message": "OnTheWirePacket received.",
                    "transferable_ranges": len(packet.transferable_ranges),
                    "revocations": len(packet.transferable_revocations),
                    "history_entries": len(packet.history.entries) if packet.history else "0",
                }
            )

        self._last_log_at = timezone.now()

    def log_not_received(self) -> None:
        """Log an error when no packet is received in the time interval defined in
        `settings.EXPECT_PACKET_EVERY`.
        """
        now = timezone.now()

        if now - self._last_log_at >= settings.EXPECT_PACKET_EVERY:
            logger.error(
                {
                    LOG_KEY: "heartbeat_not_received",
                    "message": "No data packet or heartbeat received in the last "
                    f"{settings.EXPECT_PACKET_EVERY.seconds}. "
                    "Check the health of the sender on the origin side.",
                    "EXPECT_PACKET_EVERY": f"{settings.EXPECT_PACKET_EVERY.seconds} seconds",
                }
            )

            self._last_log_at = now


def _loop() -> None:
    """Loop indefinitely until interrupted, receive packets as they become available,
    and log an error when no data packet or heartbeat is received in the defined time
    interval.
    """
    with packet_receiver.PacketReceiver() as receiver:
        handler = packet_handler.OnTheWirePacketHandler()
        keep_running = signals.BooleanCondition()
        packet_logger = _PacketLogger()

        logger.info({LOG_KEY: "receiver_ready", "message": "Ready to receive OnTheWirePackets"})

        while True:
            try:
                try:
                    packet = receiver.receive(timeout=settings.PACKET_RECEIVER_TIMEOUT)
                except packet_receiver.NothingToReceive:
                    if not keep_running:
                        break

                    packet_logger.log_not_received()
                except packet_receiver.ReceptionError as error:
                    logger.error(
                        {
                            LOG_KEY: "packet_reception_error",
                            "message": "Error on packet reception.",
                            "error": str(error),
                        }
                    )
                else:
                    LastPacketReceivedAt.update()
                    packet_logger.log_received(packet)
                    handler.handle(packet)
            except Exception as error:
                logger.error(
                    {
                        LOG_KEY: "on_the_wire_exception",
                        "message": "An unexpected error occurred while processing an OnTheWirePacket",
                        "error": str(error),
                    }
                )


def run() -> None:  # pragma: no cover
    """Entrypoint for the receiver."""

    try:
        _loop()
    finally:
        connections.close_all()


__all__ = ("run",)
