from rest_framework import serializers as drf_serializers


class MetadataSerializer(drf_serializers.Serializer):
    contact = drf_serializers.CharField(required=False)
    badge_content = drf_serializers.CharField(required=False)
    badge_color = drf_serializers.CharField(required=False)
