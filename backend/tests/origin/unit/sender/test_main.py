import datetime
import logging
from unittest import mock

import pytest
from django.conf import Settings
from django.utils import timezone

from eurydice.common import protocol
from eurydice.common.utils import signals
from eurydice.origin.sender import main, packet_generator, packet_sender
from tests.utils import process_logs


@mock.patch.object(signals.BooleanCondition, "__bool__")
@mock.patch.object(packet_generator.OnTheWirePacketGenerator, "generate_next_packet")
@mock.patch.object(packet_sender.PacketSender, "send")
@mock.patch("eurydice.origin.sender.main._heartbeat_should_be_sent")
@pytest.mark.django_db()
def test__main_running(
    patched__heartbeat_should_be_sent: mock.MagicMock,
    patched_send: mock.MagicMock,
    patched_generate_next_packet: mock.MagicMock,
    patched_running_condition_bool: mock.MagicMock,
    caplog: pytest.LogCaptureFixture,
    settings: Settings,
):
    caplog.set_level(logging.INFO)
    packets = [
        # this packet should be sent because
        # the first packet is always sent as heartbeat
        protocol.OnTheWirePacket(),
        # this packet should be sent because it is not empty
        protocol.OnTheWirePacket(history=protocol.History(entries=[])),
        # this packet should not be sent because it is empty
        protocol.OnTheWirePacket(),
    ]
    patched_generate_next_packet.side_effect = packets
    patched__heartbeat_should_be_sent.side_effect = [True, False, False]
    patched_running_condition_bool.side_effect = [True, True, True, False]

    calls = [mock.call(packets[0]), mock.call(packets[1])]

    settings.LIDIS_HOST = "127.0.0.1"
    settings.LIDIS_PORT = 666
    main._loop()

    patched_send.assert_has_calls(calls)

    log_messages = process_logs(caplog.messages)

    assert log_messages == [
        {"log_key": "sender_ready", "message": "Ready to send OnTheWirePackets"},
        {"log_key": "packet_stats", "message": "sending heartbeat"},
        {
            "log_key": "packet_stats",
            "message": "Sending OnTheWirePacket<transferable ranges: 0, revocations: 0, history entries: 0>",
        },
    ]

    assert len(log_messages) == 3


@mock.patch.object(signals.BooleanCondition, "__bool__")
@mock.patch.object(packet_generator.OnTheWirePacketGenerator, "generate_next_packet")
def test_main_not_running(
    patched_generate_next_packet: mock.MagicMock,
    patched_running_bool: mock.MagicMock,
    settings: Settings,
):
    settings.LIDIS_HOST = "127.0.0.1"
    settings.LIDIS_PORT = 666
    patched_running_bool.return_value = False
    main._loop()
    assert not patched_generate_next_packet.called


def test__heartbeat_should_be_sent_no_last_packet():
    assert main._heartbeat_should_be_sent(None) is True


@pytest.mark.parametrize(("time_delta_in_seconds", "expected_return"), [(5, False), (10, True), (11, True)])
def test__heartbeat_should_be_sent(time_delta_in_seconds: int, expected_return: bool, settings: Settings):
    settings.HEARTBEAT_SEND_EVERY = 10

    last_packet_sent_at = timezone.now() - datetime.timedelta(seconds=time_delta_in_seconds)

    assert main._heartbeat_should_be_sent(last_packet_sent_at) is expected_return


def test___log_packet_stats(caplog: pytest.LogCaptureFixture):
    caplog.set_level(logging.INFO)
    packet = protocol.OnTheWirePacket(history=protocol.History(entries=[]))
    main._log_packet_stats(packet)

    log_messages = process_logs(caplog.messages)

    assert [
        {
            "log_key": "packet_stats",
            "message": "Sending OnTheWirePacket<transferable ranges: 0, revocations: 0, history entries: 0>",
        }
    ] == log_messages


def test___log_packet_stats_empty_packet(caplog: pytest.LogCaptureFixture):
    caplog.set_level(logging.INFO)
    packet = protocol.OnTheWirePacket()
    main._log_packet_stats(packet)

    log_messages = process_logs(caplog.messages)

    assert [{"log_key": "packet_stats", "message": "sending heartbeat"}] == log_messages
