from datetime import datetime
from typing import Dict
from typing import Optional
from typing import Union

from rest_framework.generics import RetrieveAPIView

from eurydice.origin.api.docs import decorators as documentation
from eurydice.origin.api.serializers import StatusSerializer
from eurydice.origin.core import models


@documentation.sender_status
class StatusView(RetrieveAPIView):
    """
    Retrieve sender status.

    All authenticated users can retrieve the status.

    The field "maintenance" shows whether the app is in maintenance mode. In
    maintenance mode, transferables can still be submitted to the origin side but they
    aren't transferred immediately to the destination side (only heartbeats are sent).
    Transferables are sent after the end of the maintenance.

    The field "last_packet_sent_at" can be used to check whether the sender is
    healthy: it shows when the last packet - either data or heartbeat - was sent.
    (Heartbeat frequency is configured via the HEARTBEAT_SEND_EVERY environment
    variable.)
    """

    serializer_class = StatusSerializer

    def get_object(self) -> Dict[str, Union[bool, Optional[datetime]]]:
        """Get sender status data."""
        maintenance = models.Maintenance.is_maintenance()
        last_packet_sent_at = models.LastPacketSentAt.get_timestamp()
        return {
            "maintenance": maintenance,
            "last_packet_sent_at": last_packet_sent_at,
        }
