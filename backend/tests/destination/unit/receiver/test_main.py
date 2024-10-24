import datetime
import logging
from unittest import mock

import freezegun
import pytest
from django.conf import Settings
from django.utils import timezone

from eurydice.common import protocol
from eurydice.common.utils import signals
from eurydice.destination.receiver import main
from eurydice.destination.receiver import packet_handler
from eurydice.destination.receiver import packet_receiver


@pytest.fixture()
def packet() -> mock.Mock:
    return mock.Mock(autospec=protocol.OnTheWirePacket)


class TestPacketLogger:
    @pytest.mark.parametrize(
        ("is_empty", "expected_msg"),
        [(True, "Heartbeat received"), (False, "{} received")],
    )
    def test_log_received(
        self,
        is_empty: bool,
        expected_msg: str,
        packet: mock.Mock,
        caplog: pytest.LogCaptureFixture,
    ):
        caplog.set_level(logging.INFO)
        packet.is_empty.return_value = is_empty

        packet_logger = main._PacketLogger()
        packet_logger.log_received(packet)
        assert [expected_msg.format(packet)] == caplog.messages

    @freezegun.freeze_time()
    @pytest.mark.parametrize("should_log", [True, False])
    def test_log_not_received(
        self, should_log: bool, settings: Settings, caplog: pytest.LogCaptureFixture
    ):
        caplog.set_level(logging.ERROR)
        settings.EXPECT_PACKET_EVERY = datetime.timedelta(seconds=1)

        packet_logger = main._PacketLogger()

        if should_log:
            packet_logger._last_log_at = timezone.now() - settings.EXPECT_PACKET_EVERY

        packet_logger.log_not_received()

        if should_log:
            assert [
                "No data packet or heartbeat received in the last 1 second. "
                "Check the health of the sender on the origin side."
            ] == caplog.messages
        else:
            assert not caplog.messages


@mock.patch.object(main._PacketLogger, "log_not_received")
@mock.patch.object(main._PacketLogger, "log_received")
@mock.patch.object(packet_handler.OnTheWirePacketHandler, "handle")
@mock.patch.object(signals.BooleanCondition, "__bool__")
@mock.patch("eurydice.destination.receiver.main.packet_receiver.PacketReceiver")
@pytest.mark.django_db()
def test_loop_receive_packet(
    PacketReceiver: mock.Mock,  # noqa: N803
    boolean_cond: mock.Mock,
    handler: mock.Mock,
    log_received: mock.Mock,
    log_not_received: mock.Mock,
    packet: mock.Mock,
):
    receiver = mock.MagicMock(autospec=packet_receiver.PacketReceiver)
    receiver.__enter__.return_value = receiver
    receiver.receive.side_effect = [packet, packet_receiver.NothingToReceive]
    PacketReceiver.return_value = receiver

    boolean_cond.return_value = False
    main._loop()

    handler.assert_called_once_with(packet)
    log_received.assert_called_once_with(packet)
    log_not_received.assert_not_called()


@mock.patch.object(main._PacketLogger, "log_not_received")
@mock.patch.object(main._PacketLogger, "log_received")
@mock.patch.object(packet_handler.OnTheWirePacketHandler, "handle")
@mock.patch.object(signals.BooleanCondition, "__bool__")
@mock.patch("eurydice.destination.receiver.main.packet_receiver.PacketReceiver")
def test_loop_reception_error(
    PacketReceiver: mock.Mock,  # noqa: N803
    boolean_cond: mock.Mock,
    handler: mock.Mock,
    log_received: mock.Mock,
    log_not_received: mock.Mock,
    caplog: pytest.LogCaptureFixture,
):
    receiver = mock.MagicMock(autospec=packet_receiver.PacketReceiver)
    receiver.__enter__.return_value = receiver
    receiver.receive.side_effect = [
        packet_receiver.ReceptionError,
        packet_receiver.NothingToReceive,
    ]
    PacketReceiver.return_value = receiver

    boolean_cond.return_value = False
    main._loop()

    handler.assert_not_called()
    log_received.assert_not_called()
    log_not_received.assert_not_called()

    assert "Error on packet reception." in caplog.text


@mock.patch.object(main._PacketLogger, "log_not_received")
@mock.patch.object(main._PacketLogger, "log_received")
@mock.patch.object(packet_handler.OnTheWirePacketHandler, "handle")
@mock.patch.object(signals.BooleanCondition, "__bool__")
@mock.patch("eurydice.destination.receiver.main.packet_receiver.PacketReceiver")
def test_loop_reception_timeout(
    PacketReceiver: mock.Mock,  # noqa: N803
    boolean_cond: mock.Mock,
    handler: mock.Mock,
    log_received: mock.Mock,
    log_not_received: mock.Mock,
):
    receiver = mock.MagicMock(autospec=packet_receiver.PacketReceiver)
    receiver.__enter__.return_value = receiver
    receiver.receive.side_effect = [packet_receiver.NothingToReceive] * 2
    PacketReceiver.return_value = receiver

    boolean_cond.side_effect = [True, False]
    main._loop()

    handler.assert_not_called()
    log_received.assert_not_called()
    log_not_received.assert_called_once()


@mock.patch.object(main._PacketLogger, "log_not_received")
@mock.patch.object(main._PacketLogger, "log_received")
@mock.patch.object(packet_handler.OnTheWirePacketHandler, "handle")
@mock.patch.object(signals.BooleanCondition, "__bool__")
@mock.patch("eurydice.destination.receiver.main.packet_receiver.PacketReceiver")
def test_loop_unexpected_exception(
    PacketReceiver: mock.Mock,  # noqa: N803
    boolean_cond: mock.Mock,
    handler: mock.Mock,
    log_received: mock.Mock,
    log_not_received: mock.Mock,
    caplog: pytest.LogCaptureFixture,
):
    caplog.set_level(logging.ERROR)

    receiver = mock.MagicMock(autospec=packet_receiver.PacketReceiver)
    receiver.__enter__.return_value = receiver
    receiver.receive.side_effect = [
        Exception("this is terrible"),
        packet_receiver.NothingToReceive,
    ]
    PacketReceiver.return_value = receiver

    boolean_cond.side_effect = [False]
    main._loop()

    handler.assert_not_called()
    log_received.assert_not_called()
    log_not_received.assert_not_called()

    assert "this is terrible" in caplog.text
    assert (
        "An unexpected error occurred while processing an OnTheWirePacket"
        in caplog.text
    )
