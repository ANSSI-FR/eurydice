from django.conf import settings
from django.utils.translation import gettext_lazy as _
from drf_spectacular import utils as spectacular_utils
from rest_framework import status

from eurydice.common.api import serializers
from eurydice.common.api.docs import custom_spectacular
from eurydice.common.api.docs import utils as docs

login = spectacular_utils.extend_schema_view(
    get=custom_spectacular.extend_schema(
        operation_id="login",
        summary=_("Retrieve session cookie"),
        description=_((settings.COMMON_DOCS_PATH / "user-login.md").read_text()),
        parameters=[
            spectacular_utils.OpenApiParameter(
                name="set-cookie",
                location="header",
                description=_(
                    "Cookie containing the CSRF token for preventing CSRF attacks."
                ),
                response=[status.HTTP_204_NO_CONTENT],
                examples=[
                    spectacular_utils.OpenApiExample(
                        name=settings.CSRF_COOKIE_NAME,
                        value=(
                            f"{settings.CSRF_COOKIE_NAME}=wqTG4YZkCnXUqb7E4um1kV6xCSEsKSI1mpTfeWWrej7tI2DMe0qMpU8PyvsDSva3; "  # noqa: E501
                            f"expires=Wed, 22 Feb 2023 17:38:37 GMT; "
                            f"Max-Age={settings.CSRF_COOKIE_AGE}; "
                            f"Path={settings.CSRF_COOKIE_PATH}; "
                            f"SameSite={settings.CSRF_COOKIE_SAMESITE}"
                        ),
                    )
                ],
            ),
            spectacular_utils.OpenApiParameter(
                name="Set-Cookie",
                location="header",
                description=_(
                    "Cookie containing the session token "
                    "for authenticating requests from the frontend."
                ),
                response=[status.HTTP_204_NO_CONTENT],
                examples=[
                    spectacular_utils.OpenApiExample(
                        name=settings.SESSION_COOKIE_NAME,
                        value=(
                            f"{settings.SESSION_COOKIE_NAME}=67pb2vcxfgr3tyo33ascxhrxk21km51y; "  # noqa: E501
                            f"expires=Wed, 09 Mar 2022 17:38:37 GMT; "
                            f"HttpOnly; "
                            f"Max-Age={settings.SESSION_COOKIE_AGE}; "
                            f"Path={settings.SESSION_COOKIE_PATH}; "
                            f"SameSite={settings.SESSION_COOKIE_SAMESITE}"
                        ),
                    )
                ],
            ),
        ],
        responses={
            status.HTTP_204_NO_CONTENT: spectacular_utils.OpenApiResponse(
                description=_("The session cookie has been set."),
            ),
            # DRF returns an HTTP 403 error claiming credentials not found
            # when IsAuthenticated permission is used
            # see: https://github.com/encode/django-rest-framework/issues/5968
            status.HTTP_403_FORBIDDEN: docs.NotAuthenticatedResponse,
        },
        code_samples=[
            {
                "lang": "bash",
                "label": "cURL",
                "source": (
                    settings.DOCS_PATH / "cookie-auth.sh"  # type: ignore
                ).read_text(),
            }
        ],
        tags=[_("Account management")],
    )
)

user_details = spectacular_utils.extend_schema_view(
    get=custom_spectacular.extend_schema(
        operation_id="user-me",
        summary=_("Get user details"),
        description=_((settings.COMMON_DOCS_PATH / "user-me.md").read_text()),
        responses={
            status.HTTP_200_OK: spectacular_utils.OpenApiResponse(
                description=_("User is successfully authenticated."),
                response=serializers.UserSerializer,
                examples=[
                    spectacular_utils.OpenApiExample(
                        _("Get user details"),
                        value={
                            "username": "johndoe1",
                        },
                    ),
                ],
            ),
            status.HTTP_401_UNAUTHORIZED: docs.NotAuthenticatedResponse,
        },
        code_samples=[
            {
                "lang": "bash",
                "label": "cURL",
                "source": (
                    settings.DOCS_PATH / "user-me.sh"  # type: ignore
                ).read_text(),
            }
        ],
        tags=[_("Account management")],
    )
)

server_metadata = spectacular_utils.extend_schema_view(
    get=custom_spectacular.extend_schema(
        operation_id="metadata",
        summary=_("Get UI metadata"),
        tags=[_("Metadata")],
    )
)


__all__ = (
    "login",
    "user_details",
    "server_metadata",
)
