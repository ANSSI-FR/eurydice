import base64

import django.urls
import humanfriendly
import pytest
from django.contrib.auth.models import AbstractUser
from django.contrib.sessions.models import Session
from django.test import override_settings
from faker import Faker
from rest_framework import test
from rest_framework.authentication import BasicAuthentication

from eurydice.common.api.views import UserDetailsView
from tests.common.integration.factory.session import SessionFactory


@override_settings(SESSION_COOKIE_SECURE=True, CSRF_COOKIE_SECURE=True)
def user_login_sets_cookies_with_default_values(api_client: test.APIClient):
    url = django.urls.reverse("user-login")

    response = api_client.get(url, HTTP_X_REMOTE_USER="billmurray")

    assert response.status_code == 204
    assert response.data is None

    csrf_cookie = response.cookies["eurydice_csrftoken"]
    session_cookie = response.cookies["eurydice_sessionid"]

    assert csrf_cookie["samesite"] == session_cookie["samesite"] == "Strict"
    assert csrf_cookie["secure"] == session_cookie["secure"] == True  # noqa: E712

    assert session_cookie["max-age"] == humanfriendly.parse_timespan("24h")


def user_login_forbidden_without_remote_user_header(api_client: test.APIClient):
    url = django.urls.reverse("user-login")

    response = api_client.get(url)

    assert response.status_code == 403
    assert len(response.cookies) == 0
    assert response.data["detail"].code == "not_authenticated"


def user_login_basic_auth(api_client: test.APIClient, user: AbstractUser):
    # can't modify drf authentication settings at runtime, so here's a workaround
    UserDetailsView.authentication_classes = [BasicAuthentication]

    username = user.username
    password = user.password
    user.set_password(password)
    user.save()

    url = django.urls.reverse("user-me")
    response = api_client.get(url)
    assert response.status_code == 401

    valid_credentials = base64.b64encode(
        bytes(f"{username}:{password}", "utf-8")
    ).decode("utf-8")

    api_client.credentials(HTTP_AUTHORIZATION=f"Basic {valid_credentials}")
    response = api_client.get(
        url,
    )
    assert response.status_code == 200
    assert response.data["username"] == username


def user_login_removes_expired_sessions(api_client: test.APIClient, faker: Faker):
    expire_date = faker.date_time_this_decade(
        before_now=True, tzinfo=django.utils.timezone.get_current_timezone()
    )
    expired_session = SessionFactory.create(expire_date=expire_date)

    url = django.urls.reverse("user-login")

    response = api_client.get(url, HTTP_X_REMOTE_USER="billmurray")

    assert response.status_code == 204

    with pytest.raises(Session.DoesNotExist):
        Session.objects.get(session_key=expired_session.session_key)
