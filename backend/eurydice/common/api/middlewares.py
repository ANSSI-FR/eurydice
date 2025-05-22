from typing import Callable
from typing import cast

from django import http
from django.conf import settings
from django.contrib.auth import middleware
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.utils import timezone

from eurydice.common.models.user import AbstractUser


class PersistentRemoteUserMiddlewareWithCustomHeader(
    middleware.PersistentRemoteUserMiddleware
):
    """Allows DRF to authenticate with the Remote-User
    HTTP header set by the reverse proxy on all requests.

    By default DRF's RemoteUserAuthentication will use the
    value set in the REMOTE_USER env var.

    If we want authentication to be based on a custom HTTP
    header instead, we need to prefix `header` with `HTTP_`
    to tell it to look in the HTTP request headers.

    See: https://docs.djangoproject.com/en/3.2/howto/auth-remote-user/
    See: https://www.django-rest-framework.org/api-guide/authentication/#remoteuserauthentication # noqa: E501
    """

    header = settings.REMOTE_USER_HEADER


_GetResponseCallable = Callable[[HttpRequest], HttpResponse]


class AuthenticatedUserHeaderMiddleware:
    """Middleware for adding authenticated user's username to response headers"""

    def __init__(self, get_response: _GetResponseCallable) -> None:  # noqa: D101
        """Initialize the middleware with the function calling its successor in the pipeline

        Args:
            get_response: callable used to retrieve response
        """
        self.get_response = get_response

    def __call__(self, request: http.HttpRequest) -> http.HttpResponse:  # noqa: D102
        """Intercept responses and inject a header before returning them

        Args:
            request: from which to extract response

        Returns:
            the response itself
        """
        response = self.get_response(request)
        if request.user.is_authenticated:
            response.headers["Authenticated-User"] = request.user.get_username()

        return response


class LastAccessMiddleware:
    """Middleware for updating authenticated user's last_access timestamp."""

    def __init__(self, get_response: _GetResponseCallable) -> None:
        """Initialize the middleware with the function calling its successor in the pipeline

        Args:
            get_response: callable used to retrieve response
        """
        self.get_response = get_response

    def __call__(self, request: http.HttpRequest) -> http.HttpResponse:
        """Intercept requests to update the authenticated user's last_access timestamp.

        Unlike last_login, this field gets updated every time the user accesses the
        API, even when they authenticate with an API token.

        Args:
            request: from which to extract response

        Returns:
            the response itself
        """
        response = self.get_response(request)

        if request.user.is_authenticated:
            user = cast(AbstractUser, request.user)
            user.last_access = timezone.now()
            user.save(update_fields=["last_access"])

        return response


__all__ = (
    "PersistentRemoteUserMiddlewareWithCustomHeader",
    "AuthenticatedUserHeaderMiddleware",
    "LastAccessMiddleware",
)
