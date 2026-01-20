from django.conf import settings
from django.urls import path

from eurydice.common.api import views

urlpatterns = [
    path("schema", views.OpenApiViewSet, name="api-schema"),
    path("user/me/", views.UserDetailsView.as_view(), name="user-me"),
    path("user/token/", views.UserTokenView.as_view(), name="user-token"),
]

if settings.REMOTE_USER_HEADER_AUTHENTICATION_ENABLED:
    urlpatterns.append(path("user/login", views.UserLoginView.as_view(), name="user-login"))

handler400 = "rest_framework.exceptions.bad_request"
handler500 = "rest_framework.exceptions.server_error"

__all__ = ("urlpatterns", "handler400", "handler500")
