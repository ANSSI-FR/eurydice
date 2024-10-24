import datetime
from typing import Dict
from typing import Optional
from typing import Union

from django.conf import settings
from django.db.models import Count
from django.db.models import Q
from django.utils import timezone
from rest_framework import generics

from eurydice.common.api.permissions import CanViewMetrics
from eurydice.destination.api import serializers
from eurydice.destination.api.docs import decorators as documentation
from eurydice.destination.core import models


@documentation.metrics
class MetricsView(generics.RetrieveAPIView):
    """Access metrics about transferables."""

    serializer_class = serializers.RollingMetricsSerializer
    permission_classes = [CanViewMetrics]

    def get_object(self) -> Dict[str, Union[int, Optional[datetime.datetime]]]:
        """Returns rolling metrics for the view to display."""
        metrics = models.IncomingTransferable.objects.values("state").aggregate(
            ongoing_transferables=Count(
                "id", filter=Q(state=models.IncomingTransferableState.ONGOING)
            ),
            recent_successes=Count(
                "id",
                filter=Q(
                    finished_at__gt=timezone.now()
                    - datetime.timedelta(seconds=settings.METRICS_SLIDING_WINDOW),
                    state__in=(
                        models.IncomingTransferableState.SUCCESS,
                        models.IncomingTransferableState.REMOVED,
                        models.IncomingTransferableState.EXPIRED,
                    ),
                ),
            ),
            recent_errors=Count(
                "id",
                filter=Q(
                    finished_at__gt=timezone.now()
                    - datetime.timedelta(seconds=settings.METRICS_SLIDING_WINDOW),
                    state=models.IncomingTransferableState.ERROR,
                ),
            ),
        )
        metrics["last_packet_received_at"] = models.LastPacketReceivedAt.get_timestamp()
        return metrics


__all__ = ("MetricsView",)
