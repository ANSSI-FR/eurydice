import socket
import time

import pytest
from django.test import override_settings

from eurydice.destination.receiver import packet_receiver
from tests.common.integration.factory import protocol as protocol_factory
from tests.utils import process_logs


@override_settings(PACKET_RECEIVER_PORT=0)
def test_packet_receiver_success():
    receiver = packet_receiver.PacketReceiver()
    receiver.start()

    receiver_port = receiver._receiver_thread._server.server_address[1]

    packet = protocol_factory.OnTheWirePacketFactory()
    with socket.create_connection(("127.0.0.1", receiver_port)) as conn:
        conn.sendall(packet.to_bytes())

    assert receiver.receive() == packet

    receiver.stop()
    assert not receiver._receiver_thread.is_alive()
    assert receiver._queue.empty()


@override_settings(PACKET_RECEIVER_PORT=0)
def test_packet_receiver_context_manager_success():
    with packet_receiver.PacketReceiver() as receiver:
        packet = protocol_factory.OnTheWirePacketFactory()

        receiver_port = receiver._receiver_thread._server.server_address[1]
        with socket.create_connection(("127.0.0.1", receiver_port)) as conn:
            conn.sendall(packet.to_bytes())

        assert receiver.receive() == packet
        assert receiver._queue.empty()


@override_settings(PACKET_RECEIVER_PORT=0, RECEIVER_BUFFER_MAX_ITEMS=12)
def test_packet_receiver_receive_multiple_successively_success():
    packets = [protocol_factory.OnTheWirePacketFactory() for _ in range(10)]

    with packet_receiver.PacketReceiver() as receiver:
        receiver_port = receiver._receiver_thread._server.server_address[1]
        for packet in packets:
            with socket.create_connection(("127.0.0.1", receiver_port)) as conn:
                conn.sendall(packet.to_bytes())

            assert packet == receiver.receive()

        assert receiver._queue.empty()


@override_settings(PACKET_RECEIVER_PORT=0, RECEIVER_BUFFER_MAX_ITEMS=4)
def test_packet_receiver_receive_multiple_overflow(caplog: pytest.LogCaptureFixture):
    packets = [protocol_factory.OnTheWirePacketFactory() for _ in range(10)]

    expected_hits = 4
    expected_misses = len(packets) - expected_hits

    with packet_receiver.PacketReceiver() as receiver:
        receiver_port = receiver._receiver_thread._server.server_address[1]
        for packet in packets:
            with socket.create_connection(("127.0.0.1", receiver_port)) as conn:
                conn.sendall(packet.to_bytes())

        # wait for the receiving thread to read all data
        time.sleep(0.1)

        for nb_received, packet in enumerate(packets):
            if nb_received < expected_hits:
                assert packet == receiver.receive(block=False)
            else:
                with pytest.raises(packet_receiver.NothingToReceive):
                    receiver.receive(block=False)

        log_messages = process_logs(caplog.messages)
        errors = [error for error in log_messages if error["log_key"] == "dropped_transferable"]
        assert len(errors) == expected_misses

        assert receiver._queue.empty()


@override_settings(PACKET_RECEIVER_PORT=0, RECEIVER_BUFFER_MAX_ITEMS=12)
def test_packet_receiver_receive_batch_success():
    packets = [protocol_factory.OnTheWirePacketFactory() for _ in range(10)]

    with packet_receiver.PacketReceiver() as receiver:
        receiver_port = receiver._receiver_thread._server.server_address[1]
        for packet in packets:
            with socket.create_connection(("127.0.0.1", receiver_port)) as conn:
                conn.sendall(packet.to_bytes())

        for packet in packets:
            assert packet == receiver.receive()

        assert receiver._queue.empty()


@override_settings(PACKET_RECEIVER_PORT=0)
def test_packet_receiver_error_raise_ReceptionError():  # noqa: N802
    with packet_receiver.PacketReceiver() as receiver:
        receiver_port = receiver._receiver_thread._server.server_address[1]
        with socket.create_connection(("127.0.0.1", receiver_port)) as conn:
            conn.sendall(b"hello, world")

        with pytest.raises(packet_receiver.ReceptionError):
            receiver.receive()


@pytest.mark.parametrize(("block", "timeout"), [(False, 0), (True, 0.01)])
def test_packet_receiver_error_raise_NothingToReceive(  # noqa: N802
    block: bool, timeout: float
):
    with packet_receiver.PacketReceiver() as receiver:  # noqa: SIM117
        with pytest.raises(packet_receiver.NothingToReceive):
            receiver.receive(block, timeout)
