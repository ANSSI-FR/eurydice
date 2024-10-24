from django.conf import settings
from rest_framework import authentication


class RemoteUserAuthenticationWithCustomHeader(authentication.RemoteUserAuthentication):
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

    def __init__(self) -> None:
        super().__init__()
        self.header = settings.REMOTE_USER_HEADER
