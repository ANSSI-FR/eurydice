from django.conf import settings
from django.utils.translation import gettext_lazy as _
from drf_spectacular import utils as spectacular_utils
from drf_spectacular import views
from rest_framework import permissions
from rest_framework import status

OpenApiViewSet = spectacular_utils.extend_schema_view(
    get=spectacular_utils.extend_schema(
        summary=_("Retrieve the API contract"),
        description=_((settings.COMMON_DOCS_PATH / "openapi-retrieve.md").read_text()),
        tags=[
            _("OpenApi3 documentation"),
        ],
        responses={
            status.HTTP_200_OK: spectacular_utils.OpenApiResponse(
                description=_(
                    "The OpenApi3 document was successfully generated in the "
                    "requested format."
                ),
            ),
        },
    ),
)(views.SpectacularAPIView).as_view(
    # Allow anyone to view all API endpoints in specification schema
    serve_public=True,
    # Allow anyone to view the API specification schema
    permission_classes=[permissions.AllowAny],
    # Allow retrieving JSON or YAML schema, default to JSON
    renderer_classes=[
        views.OpenApiJsonRenderer2,  # type: ignore
        views.OpenApiYamlRenderer2,  # type: ignore
    ],
)
