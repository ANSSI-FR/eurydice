from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers as drf_serializers

from eurydice.common import enums
from eurydice.common.api import serializers
from eurydice.origin.core import models


class StatusSerializer(drf_serializers.Serializer):
    maintenance = drf_serializers.BooleanField(
        help_text=_("Whether the sender is currently in maintenance mode"),
    )
    last_packet_sent_at = drf_serializers.DateTimeField(
        help_text=_("The date the last packet was sent (either data or heartbeat)")
    )


class RollingMetricsSerializer(drf_serializers.Serializer):
    pending_transferables = drf_serializers.IntegerField(
        help_text=_("The amount of transferables currently waiting to be transferred"),
        min_value=0,
    )
    ongoing_transferables = drf_serializers.IntegerField(
        help_text=_("The amount of transferables currently being transferred"),
        min_value=0,
    )
    recent_successes = drf_serializers.IntegerField(
        help_text=_(
            "The amount of transferables successfully transferred within the "
            "last few minutes"
        ),
        min_value=0,
    )
    recent_errors = drf_serializers.IntegerField(
        help_text=_(
            "The amount of transferables that failed to be transferred within the "
            "last few minutes"
        ),
        min_value=0,
    )
    queue_size = drf_serializers.IntegerField(
        help_text=_("The amount of bytes currently waiting to be transferred"),
        min_value=0,
    )
    last_packet_sent_at = drf_serializers.DateTimeField(
        help_text=_("The date the last packet was sent (either data or heartbeat)"),
    )


class OutgoingTransferableSerializer(drf_serializers.ModelSerializer):
    state = drf_serializers.ChoiceField(
        # __iter__ for this enum is overridden by the str subclassing
        # so we are using __members__ to iterate over enum key values
        [state.value for state in enums.OutgoingTransferableState],
        help_text=_("The state of this Transferable"),
    )

    progress = drf_serializers.IntegerField(
        help_text=_(
            "The percentage of bytes for this Transferable that have been "
            "sent through the network diode"
        ),
        min_value=0,
        max_value=100,
    )

    submission_succeeded = drf_serializers.BooleanField(
        help_text=_("Whether the submission of the file by the user succeeded")
    )

    bytes_transferred = drf_serializers.IntegerField(
        source="auto_bytes_transferred",
        help_text=_("The amount of bytes transferred through the network diode"),
        min_value=0,
        max_value=settings.TRANSFERABLE_MAX_SIZE,
    )

    speed = drf_serializers.IntegerField(
        help_text=_("The transfer speed through the network diode in bytes per second"),
        min_value=0,
        allow_null=True,
    )

    sha1 = serializers.BytesAsHexadecimalField(
        # example value
        default=b"7\xf0+\xcbK\xaa\x83\xeePr|\xfe\xc3n\xdf>\xfa\xe2S<",
        allow_null=True,
        help_text=_("SHA-1 digest for this transferable in hexadecimal form"),
    )

    finished_at = drf_serializers.DateTimeField(
        help_text=_("Date at which this transferable was fully sent through the diode"),
        allow_null=True,
    )

    estimated_finish_date = drf_serializers.DateTimeField(
        help_text=_(
            "Date at which this transferable is expected to be fully"
            " sent through the diode."
        ),
        allow_null=True,
    )

    class Meta:
        model = models.OutgoingTransferable
        fields = (
            "id",
            "created_at",
            "name",
            "sha1",
            "size",
            "user_provided_meta",
            "submission_succeeded",
            "submission_succeeded_at",
            "state",
            "progress",
            "bytes_transferred",
            "finished_at",
            "speed",
            "estimated_finish_date",
        )


__all__ = ("OutgoingTransferableSerializer", "RollingMetricsSerializer")
