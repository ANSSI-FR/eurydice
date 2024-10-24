import pytest
from faker import Faker
from rest_framework import test

from tests.common.integration.endpoints import login
from tests.origin.integration import factory


@pytest.mark.django_db()
def test_user_login_sets_cookies_with_default_values(api_client: test.APIClient):
    login.user_login_sets_cookies_with_default_values(api_client)


@pytest.mark.django_db()
def test_user_login_forbidden_without_remote_user_header(api_client: test.APIClient):
    login.user_login_forbidden_without_remote_user_header(api_client)


@pytest.mark.django_db()
def test_user_login_basic_auth(api_client: test.APIClient):
    user = factory.UserFactory()
    login.user_login_basic_auth(api_client, user)


@pytest.mark.django_db()
def test_user_login_removes_expired_sessions(api_client: test.APIClient, faker: Faker):
    login.user_login_removes_expired_sessions(api_client, faker)
