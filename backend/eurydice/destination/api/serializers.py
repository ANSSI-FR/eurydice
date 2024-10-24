from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from eurydice.common.api import serializers as common_serializers
from eurydice.destination.core import models


class StatusSerializer(serializers.Serializer):
    last_packet_received_at = serializers.DateTimeField(
        help_text=_("The date the last packet was received (either data or heartbeat)")
    )


class RollingMetricsSerializer(serializers.Serializer):
    ongoing_transferables = serializers.IntegerField(
        help_text=_("The amount of transferables currently being transferred"),
        min_value=0,
    )
    recent_successes = serializers.IntegerField(
        help_text=_(
            "The amount of transferables successfully transferred within the "
            "last few minutes"
        ),
        min_value=0,
    )
    recent_errors = serializers.IntegerField(
        help_text=_(
            "The amount of transferables that failed to be transferred within the "
            "last few minutes"
        ),
        min_value=0,
    )
    last_packet_received_at = serializers.DateTimeField(
        help_text=_("The date the last packet was received (either data or heartbeat)")
    )


class IncomingTransferableSerializer(serializers.ModelSerializer):
    sha1 = common_serializers.BytesAsHexadecimalField(
        # example value
        default=b"7\xf0+\xcbK\xaa\x83\xeePr|\xfe\xc3n\xdf>\xfa\xe2S<",
        allow_null=True,
        help_text=_("SHA-1 digest for this transferable in hexadecimal form"),
    )

    progress = serializers.IntegerField(
        help_text=_(
            "The percentage of bytes for this Transferable that have been "
            "received from the network diode"
        ),
        min_value=0,
        max_value=100,
    )

    expires_at = serializers.DateTimeField(
        help_text=_("The Transferable will be available until that date"),
        allow_null=True,
    )

    class Meta:
        model = models.IncomingTransferable
        fields = (
            "id",
            "created_at",
            "name",
            "sha1",
            "size",
            "user_provided_meta",
            "state",
            "progress",
            "finished_at",
            "expires_at",
            "bytes_received",
        )


__all__ = (
    "IncomingTransferableSerializer",
    "RollingMetricsSerializer",
    "StatusSerializer",
)
