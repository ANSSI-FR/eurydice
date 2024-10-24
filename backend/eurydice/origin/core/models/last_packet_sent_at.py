from eurydice.common import models as common_models


class LastPacketSentAt(common_models.TimestampSingleton):
    """Singleton holding the date of the last sent packet (data or heartbeat)."""

    class Meta:
        db_table = "eurydice_last_packet_sent_at"
