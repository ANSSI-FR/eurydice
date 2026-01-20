from rest_framework import serializers as drf_serializers


class MetadataSerializer(drf_serializers.Serializer):
    contact = drf_serializers.CharField(required=False)
    badge_content = drf_serializers.CharField(required=False)
    badge_color = drf_serializers.CharField(required=False)
    encryption_enabled = drf_serializers.BooleanField(default=False)
    public_key = drf_serializers.CharField(required=False)
