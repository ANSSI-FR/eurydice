from drf_spectacular import types
from drf_spectacular import utils
from rest_framework import serializers


@utils.extend_schema_field(types.OpenApiTypes.STR)
class BytesAsHexadecimalField(serializers.Field):
    """Hexadecimal string serializer for binary field."""

    def to_representation(self, value: bytes) -> str:
        """
        Args:
            value (bytes): bytes to convert to hexadecimal string.

        Returns:
            str: hexadecimal string from binary value.

        """
        return value.hex()

    def to_internal_value(self, data: str) -> bytes:
        """
        Args:
            data (str): hexadecimal string to convert to binary value.

        Returns:
            bytes: bytes converted from hexadecimal string.

        """
        return bytes.fromhex(data)


__all__ = ("BytesAsHexadecimalField",)
