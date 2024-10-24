import datetime
from typing import Dict
from typing import Optional
from typing import Union

from django.conf import settings
from django.db.models import Count
from django.db.models import Q
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.utils import timezone
from rest_framework import generics

from eurydice.common.api.permissions import CanViewMetrics
from eurydice.common.enums import OutgoingTransferableState
from eurydice.origin.api import serializers
from eurydice.origin.api.docs import decorators as documentation
from eurydice.origin.core import enums
from eurydice.origin.core import models


@documentation.metrics
class MetricsView(generics.RetrieveAPIView):
    """Access metrics about transferables."""

    serializer_class = serializers.RollingMetricsSerializer
    permission_classes = [CanViewMetrics]

    def get_object(self) -> Dict[str, Union[int, Optional[datetime.datetime]]]:
        """Returns rolling metrics for the view to display."""
        return {
            **models.OutgoingTransferable.objects_with_state_only.values(
                "state"
            ).aggregate(
                pending_transferables=Count(
                    "id", filter=Q(state=OutgoingTransferableState.PENDING)
                ),
                ongoing_transferables=Count(
                    "id", filter=Q(state=OutgoingTransferableState.ONGOING)
                ),
                recent_successes=Count(
                    "id",
                    filter=Q(
                        auto_state_updated_at__gt=timezone.now()
                        - datetime.timedelta(seconds=settings.METRICS_SLIDING_WINDOW),
                        state=OutgoingTransferableState.SUCCESS,
                    ),
                ),
                recent_errors=Count(
                    "id",
                    filter=Q(
                        auto_state_updated_at__gt=timezone.now()
                        - datetime.timedelta(seconds=settings.METRICS_SLIDING_WINDOW),
                        state=OutgoingTransferableState.ERROR,
                    ),
                ),
            ),
            **models.TransferableRange.objects.aggregate(
                queue_size=Coalesce(
                    Sum(
                        "size",
                        filter=Q(
                            transfer_state=enums.TransferableRangeTransferState.PENDING
                        ),
                    ),
                    0,
                )
            ),
            "last_packet_sent_at": models.LastPacketSentAt.get_timestamp(),
        }


__all__ = ("MetricsView",)
