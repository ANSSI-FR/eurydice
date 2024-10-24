import queue

import django.conf
import pytest

from eurydice.origin.sender import packet_sender


class Test_SenderThread:  # noqa: N801
    def test_run_stop_with_poison_pill(self):
        qu = queue.Queue(maxsize=1)
        thread = packet_sender._SenderThread(qu)
        qu.put(None, block=False)
        thread.run()
        assert qu.empty()

    def test_run_log_error(
        self, settings: django.conf.Settings, caplog: pytest.LogCaptureFixture
    ):
        settings.LIDIS_HOST, settings.LIDIS_PORT = "localhost", 1
        qu = queue.Queue(maxsize=2)
        thread = packet_sender._SenderThread(qu)
        qu.put(b"Lorem ipsum dolor sit amet", block=False)
        qu.put(None, block=False)
        thread.run()
        assert qu.empty()
        assert "Failed to send data through the socket." in caplog.text
