import socketserver
from typing import Iterator, Type
from unittest import mock

import django.conf
import pytest
from faker import Faker

from eurydice.common import protocol
from eurydice.origin.sender import packet_sender


@pytest.fixture()
def RequestHandler() -> Type:  # noqa: N802
    class _RequestHandler(socketserver.StreamRequestHandler):
        received = []

        def handle(self):
            _RequestHandler.received.append(self.rfile.read())

    return _RequestHandler


@pytest.fixture()
def server(RequestHandler: Type) -> Iterator[socketserver.TCPServer]:  # noqa: N803
    with socketserver.TCPServer(("localhost", 0), RequestHandler) as s:
        yield s


@pytest.fixture()
def sender(server: socketserver.TCPServer, settings: django.conf.Settings) -> packet_sender.PacketSender:
    settings.LIDIS_HOST, settings.LIDIS_PORT = server.socket.getsockname()
    return packet_sender.PacketSender()


def test_packet_sender_success(sender: packet_sender.PacketSender, server: socketserver.TCPServer):
    packet = protocol.OnTheWirePacket()

    sender.start()
    sender.send(packet)
    server.handle_request()
    sender.stop()

    assert len(server.RequestHandlerClass.received) == 1
    received_data = server.RequestHandlerClass.received[0]
    assert received_data == packet.to_bytes()
    assert not sender._sender_thread.is_alive()
    assert sender._queue.empty()


def test_packet_sender_context_manager_success(sender: packet_sender.PacketSender, server: socketserver.TCPServer):
    packet = protocol.OnTheWirePacket()

    with sender as s:
        s.send(packet)
        server.handle_request()

    assert len(server.RequestHandlerClass.received) == 1
    received_data = server.RequestHandlerClass.received[0]
    assert received_data == packet.to_bytes()
    assert not sender._sender_thread.is_alive()
    assert sender._queue.empty()


def test_packet_sender_send_multiple_times_success(
    sender: packet_sender.PacketSender, server: socketserver.TCPServer, faker: Faker
):
    with sender as s:
        for i in range(10):
            packet = mock.create_autospec(protocol.OnTheWirePacket)
            serialized_packet = faker.binary(faker.pyint(min_value=1, max_value=100))
            packet.to_bytes.return_value = serialized_packet

            s.send(packet)
            server.handle_request()

            assert len(server.RequestHandlerClass.received) == i + 1
            assert server.RequestHandlerClass.received[i] == serialized_packet

    assert not sender._sender_thread.is_alive()
    assert sender._queue.empty()


def test_packet_sender_error_thread_not_running(settings: django.conf.Settings):
    settings.LIDIS_HOST, settings.LIDIS_PORT = "localhost", 1

    sender = packet_sender.PacketSender()
    sender.start()
    sender.stop()

    with pytest.raises(packet_sender.SenderThreadNotRunningError):
        sender.send(protocol.OnTheWirePacket())
