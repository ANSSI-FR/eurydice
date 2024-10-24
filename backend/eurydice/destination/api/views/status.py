import datetime
from typing import Dict
from typing import Optional

from rest_framework import generics

from eurydice.destination.api import serializers
from eurydice.destination.api.docs import decorators as documentation
from eurydice.destination.core import models


@documentation.receiver_status
class StatusView(generics.RetrieveAPIView):
    """
    Retrieve receiver status.

    All authenticated users can retrieve the status.
    """

    serializer_class = serializers.StatusSerializer

    def get_object(self) -> Dict[str, Optional[datetime.datetime]]:
        """Get receiver status data."""
        last_packet_received_at = models.LastPacketReceivedAt.get_timestamp()
        return {
            "last_packet_received_at": last_packet_received_at,
        }


__all__ = ("StatusView",)
