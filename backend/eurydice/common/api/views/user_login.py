from django.core import management
from django.utils import decorators as django_decorators
from rest_framework import permissions
from rest_framework import request as drf_request
from rest_framework import response as drf_response
from rest_framework import status
from rest_framework import views

from eurydice.common.api import authentication
from eurydice.common.api import middlewares
from eurydice.common.api.docs import decorators as documentation

remote_user_auth = django_decorators.decorator_from_middleware(
    middlewares.PersistentRemoteUserMiddlewareWithCustomHeader
)


@documentation.login
@django_decorators.method_decorator(remote_user_auth, name="dispatch")
class UserLoginView(views.APIView):
    """View responsible for setting session and CSRF cookies."""

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.RemoteUserAuthenticationWithCustomHeader]

    def get(
        self, request: drf_request.Request, *args, **kwargs
    ) -> drf_response.Response:
        """Sets a session cookie and clears expired sessions for all users."""
        management.call_command("clearsessions")
        return drf_response.Response(status=status.HTTP_204_NO_CONTENT)
