from django.conf import settings
from rest_framework import generics, permissions
from rest_framework.request import Request
from rest_framework.response import Response

from eurydice.common.api.docs import decorators as documentation
from eurydice.common.api.docs import serializers as docs_serializers


@documentation.server_metadata
class ServerMetadataView(generics.GenericAPIView):
    """Get configurable metadata for the UI."""

    permission_classes = [permissions.AllowAny]
    serializer_class = docs_serializers.MetadataSerializer

    def get(self, request: Request) -> Response:
        """Get configurable metadata for the UI, such as contact info,
        banner content and banner color.

        NB: You may also find contact information at the top of the API documentation.
        """
        return Response(
            {
                "contact": settings.EURYDICE_CONTACT_FR,
                "badge_content": settings.UI_BADGE_CONTENT,
                "badge_color": settings.UI_BADGE_COLOR,
            }
        )
