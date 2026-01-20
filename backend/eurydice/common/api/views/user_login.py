from django.core import management
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.utils import decorators as django_decorators
from rest_framework import permissions, views
from rest_framework import request as drf_request

from eurydice.common.api import authentication, middlewares
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

    def get(self, request: drf_request.Request, *args, **kwargs) -> HttpResponseRedirect:
        """Sets a session cookie and clears expired sessions for all users."""
        management.call_command("clearsessions")
        # need to redirect in case of some authentication cases (with Keycloak for example)
        return redirect("/")
