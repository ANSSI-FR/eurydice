from eurydice.common import models as common_models


class LastPacketReceivedAt(common_models.TimestampSingleton):
    """Singleton holding the date of the last received packet (data or heartbeat)."""

    class Meta:
        db_table = "eurydice_last_packet_received_at"
