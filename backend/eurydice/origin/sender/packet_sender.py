import datetime
import logging
import queue
import socket
import threading
from types import TracebackType
from typing import Optional
from typing import Type

from django.conf import settings
from django.utils import timezone

from eurydice.common import protocol

logger = logging.getLogger(__name__)


class SenderThreadNotRunningError(RuntimeError):
    """Raised when the sender thread is expected to be running but is not."""


def _send_through_socket(data: bytes) -> None:
    address = (settings.LIDIS_HOST, settings.LIDIS_PORT)
    with socket.create_connection(address) as conn:
        logger.debug(
            f"Start sending data to {settings.LIDIS_HOST}:{settings.LIDIS_PORT}."
        )
        conn.sendall(data)
        logger.debug("Data successfully sent.")


def _is_poison_pill(data: Optional[bytes]) -> bool:
    """Tell whether the data inputted is a 'poison pill' i.e. a packet signaling that
    the sender thread must stop.

    """
    return data is None


class _SenderThread(threading.Thread):
    def __init__(self, sending_queue: queue.Queue):
        super().__init__()
        self._queue = sending_queue

    def run(self) -> None:
        while True:
            data = self._queue.get(block=True)

            if _is_poison_pill(data):
                break

            try:
                _send_through_socket(data)
            except socket.error:
                logger.exception("Failed to send data through the socket.")


class PacketSender:
    """Serialize OnTheWirePackets and send them to a Lidi sender service through
    a TCP socket using a sender thread.

    Attributes:
        last_packet_sent_at:    date at which last packet was sent, None if no packets
                                have been sent

    Example:
        >>> with packet_sender.PacketSender() as s:
        ...     s.send(on_the_wire_packet)

    """

    def __init__(self) -> None:
        self._queue: queue.Queue = queue.Queue(
            maxsize=settings.PACKET_SENDER_QUEUE_SIZE
        )
        self._sender_thread = _SenderThread(self._queue)
        self.last_packet_sent_at: Optional[datetime.datetime] = None

    def start(self) -> None:
        """Start the PacketSender i.e. start the sender thread.

        A PacketSender cannot be stopped then restarted. A new object must be created.

        """
        self._sender_thread.start()

    def stop(self) -> None:
        """Stop the PacketSender i.e. ask the sender thread to stop and wait for it to
        stop.

        The sender thread will stop and this method will return when there is no more
        data packet waiting to be sent in the queue.

        """
        self._send_poison_pill()
        self._sender_thread.join()

    def send(self, packet: protocol.OnTheWirePacket) -> None:
        """Submit a OnTheWirePacket for being sent by the PacketSender.

        Args:
            packet: the OnTheWirePacket to send.

        Raises:
            SenderThreadNotRunningError: if the sender thread is not running, either
            because the PacketSender has not been started, has been stopped,
            or because the sender thread encountered a problem at runtime.

        """
        if not self._sender_thread.is_alive():
            raise SenderThreadNotRunningError()

        self._queue.put(packet.to_bytes(), block=True)
        self.last_packet_sent_at = timezone.now()

    def _send_poison_pill(self) -> None:
        """Send a poison pill packet to ask the sender thread to stop."""
        self._queue.put(None, block=True)

    def __enter__(self) -> "PacketSender":
        self.start()
        return self

    def __exit__(
        self,
        exctype: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        exc_traceback: Optional[TracebackType],
    ) -> None:
        self.stop()


__all__ = ("PacketSender",)
