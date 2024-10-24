import django.urls
import pytest
from rest_framework import status
from rest_framework import test

from tests.origin.integration import factory
from tests.utils import fake


@pytest.mark.django_db()
def test_http_header_with_authenticated_username_is_present_on_success(
    api_client: test.APIClient,
):
    user = factory.UserProfileFactory.create().user
    url = django.urls.reverse("transferable-list")
    api_client.force_login(user=user)

    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response["Authenticated-User"] == user.username


class TestHttpHeaderOnFailure(test.APITransactionTestCase):
    def test_http_header_with_authenticated_username_is_present_on_failure(self):
        user = factory.UserProfileFactory.create().user
        url = django.urls.reverse("transferable-detail", kwargs={"pk": fake.uuid4()})
        self.client.force_login(user=user)

        response = self.client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response["Authenticated-User"] == user.username


@pytest.mark.django_db()
def test_http_header_with_authenticated_username_is_not_present_when_not_authenticated(
    api_client: test.APIClient,
):
    url = django.urls.reverse("transferable-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert not response.has_header("Authenticated-User")
