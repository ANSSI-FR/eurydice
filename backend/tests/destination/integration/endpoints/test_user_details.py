import django.urls
import pytest
from rest_framework import status
from rest_framework import test

from tests.destination.integration import factory


@pytest.mark.django_db()
def user_details_returns_username(api_client: test.APIClient):
    user = factory.UserFactory()
    api_client.force_login(user=user)
    url = django.urls.reverse("user-details")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["username"] == user.username


@pytest.mark.django_db()
def user_details_returns_401_when_not_authenticated(api_client: test.APIClient):
    url = django.urls.reverse("user-details")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert not response.has_header("Authenticated-User")
