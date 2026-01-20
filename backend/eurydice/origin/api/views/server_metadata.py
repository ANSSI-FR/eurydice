import base64
from pathlib import Path

from django.conf import settings
from rest_framework import generics, permissions
from rest_framework.request import Request
from rest_framework.response import Response

from eurydice.common.api.docs import decorators as documentation
from eurydice.common.api.docs import serializers as docs_serializers
from eurydice.common.logging.logger import LOG_KEY, logger

encoded_pubkey = ""
if hasattr(settings, "ENCRYPTION_ENABLED") and settings.ENCRYPTION_ENABLED:
    try:
        pubkey = Path(settings.PUBKEY_PATH).read_bytes()
        encoded_pubkey = base64.b64encode(pubkey).decode("utf-8")
    except FileNotFoundError as e:
        logger.error(
            {
                LOG_KEY: "public_key_error",
                "message": f"Encryption is enabled but public key file is missing at {settings.PUBKEY_PATH}.",
            }
        )
        raise RuntimeError("Missing public key file for encryption.") from e


@documentation.server_metadata
class ServerMetadataView(generics.GenericAPIView):
    """Get configurable metadata for the UI."""

    permission_classes = [permissions.AllowAny]
    serializer_class = docs_serializers.MetadataSerializer

    def get(self, request: Request) -> Response:
        """Get configurable metadata for the UI, such as contact info,
        banner content, banner color and encryption config.

        NB: You may also find contact information at the top of the API documentation.
        """
        pubkey = Path(settings.PUBKEY_PATH).read_bytes()
        encoded_pubkey = base64.b64encode(pubkey).decode("utf-8")

        return Response(
            {
                "contact": settings.EURYDICE_CONTACT_FR,
                "badge_content": settings.UI_BADGE_CONTENT,
                "badge_color": settings.UI_BADGE_COLOR,
                "encryption_enabled": getattr(settings, "ENCRYPTION_ENABLED", False),
                "encoded_public_key": encoded_pubkey,
            }
        )
