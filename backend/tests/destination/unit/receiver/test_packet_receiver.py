import queue
import socket
from unittest import mock

import pytest
from django.conf import settings

from eurydice.destination.receiver import packet_receiver


class Test_Server:  # noqa: N801
    @mock.patch.object(packet_receiver._RequestHandler, "handle")
    def test_handle_error_is_logged(
        self, mocked_handle_func: mock.Mock, caplog: pytest.LogCaptureFixture
    ):
        exc_msg = "Something terrible happened"
        mocked_handle_func.side_effect = Exception(exc_msg)

        with packet_receiver._Server(receiving_queue=mock.Mock()) as server:
            with socket.create_connection(
                ("127.0.0.1", settings.PACKET_RECEIVER_PORT)
            ) as conn:
                conn.sendall(b"hello, world")

            server.handle_request()

        assert exc_msg in caplog.text


class Test_ReceiverThread:  # noqa: N801
    def test_run_and_stop(self):
        mocked_queue = mock.create_autospec(queue.Queue)
        thread = packet_receiver._ReceiverThread(mocked_queue)
        thread.start()
        assert thread.is_alive()
        thread.stop()
        thread.join()
        assert not thread.is_alive()
