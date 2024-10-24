import logging
import queue
import socketserver
import threading
from socket import socket
from types import TracebackType
from typing import Optional
from typing import Tuple
from typing import Type
from typing import Union

from django.conf import settings

from eurydice.common import protocol

logger = logging.getLogger(__name__)


class _RequestHandler(socketserver.StreamRequestHandler):
    server: "_Server"

    def handle(self) -> None:
        """Put the data of each socket request in the server queue."""
        try:
            self.server.queue.put(
                self.rfile.read(), block=False
            )  # pytype: disable=attribute-error
        except queue.Full:
            logger.error(
                "Dropped Transferable - Receiver received data while "
                "processing queue is at full capacity"
            )
        else:
            logger.debug("New block added to queue.")


class _Server(socketserver.TCPServer):
    def __init__(self, receiving_queue: queue.Queue):
        self.queue = receiving_queue
        super().__init__(
            server_address=(
                settings.PACKET_RECEIVER_HOST,
                settings.PACKET_RECEIVER_PORT,
            ),
            RequestHandlerClass=_RequestHandler,
        )

    def handle_error(
        self,
        request: Union[socket, Tuple[bytes, socket]],
        client_address: Union[Tuple[str, int], str],
    ) -> None:
        """Log the exception arising when a socket request fails."""
        logger.exception(
            f"Exception occurred during processing of request from {client_address}"
        )


class _ReceiverThread(threading.Thread):
    def __init__(self, receiving_queue: queue.Queue):
        self._queue = receiving_queue
        self._server = _Server(self._queue)
        super().__init__()

    def run(self) -> None:
        with self._server as server:
            server.serve_forever()

    def stop(self) -> None:
        """Stop the server loop and incidentally the thread."""
        self._server.shutdown()


class ReceptionError(RuntimeError):
    """Signal an error encountered while trying to get an OnTheWirePacket from the
    PacketReceiver.
    """


class NothingToReceive(RuntimeError):
    """No packet can be obtained from the PacketReceiver at this time."""


class PacketReceiver:
    """Receive serialized OnTheWirePackets using a receiver thread running a TCP server,
    and deserialize the packets.

    Example:
        >>> with packet_receiver.PacketReceiver() as r:
        ...     packet = r.receive(timeout=0.1)

    """

    def __init__(self) -> None:
        self._queue: queue.Queue = queue.Queue(
            maxsize=settings.RECEIVER_BUFFER_MAX_ITEMS
        )
        self._receiver_thread = _ReceiverThread(self._queue)

    def start(self) -> None:
        """Start the PacketReceiver i.e. start the receiver thread.

        A PacketReceiver cannot be stopped then restarted. A new object must be created.

        """
        self._receiver_thread.start()

    def stop(self) -> None:
        """Stop the PacketReceiver i.e. ask the receiver thread to stop and wait
        for it to stop.

        """
        self._receiver_thread.stop()
        self._receiver_thread.join()

    def receive(
        self, block: bool = True, timeout: Optional[float] = None
    ) -> protocol.OnTheWirePacket:
        """Receive and deserialize an OnTheWirePacket.

        Args:
            block: whether to block until a packet is available (if timeout=None) or at
                most timeout seconds. If block is False, timeout is ignored.
            timeout: how long to block (in seconds). None means block until
                a packet is available.

        Returns:
            The received and deserialized OnTheWirePacket.

        Raises:
            NothingToReceive: if no packet is available at the end of the blocking
                period.
            ReceptionError: if an error is encountered while trying to deserialize
                an OnTheWirePacket from received data.

        """
        try:
            data = self._queue.get(block, timeout)
        except queue.Empty:
            raise NothingToReceive

        try:
            return protocol.OnTheWirePacket.from_bytes(data)
        except protocol.DeserializationError as exc:
            raise ReceptionError from exc

    def __enter__(self):
        self.start()
        return self

    def __exit__(
        self,
        exctype: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        exc_traceback: Optional[TracebackType],
    ) -> None:
        self.stop()


__all__ = (
    "ReceptionError",
    "NothingToReceive",
    "PacketReceiver",
)
