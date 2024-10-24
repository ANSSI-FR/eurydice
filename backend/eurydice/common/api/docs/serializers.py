from rest_framework import serializers as drf_serializers


class ContactSerializer(drf_serializers.Serializer):
    contact = drf_serializers.CharField()
