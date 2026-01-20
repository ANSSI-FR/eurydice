from django.urls import reverse
from rest_framework import status, test

from tests.destination.integration import factory


def get_api_token(api_client: test.APIClient):
    url = reverse("user-token")
    user = factory.UserProfileFactory.create().user
    api_client.force_login(user=user)

    # get token
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK, response.status_code
    assert "token" in response.data
    assert len(response.data["token"]) > 0
    current_token = response.data["token"]

    # renew token
    response = api_client.delete(url)
    assert "token" in response.data
    assert len(response.data["token"]) > 0
    assert current_token != response.data["token"]
