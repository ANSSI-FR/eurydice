import django.urls
import pytest
from rest_framework import status, test


@pytest.mark.django_db()
def test_post_association_token_success(api_client: test.APIClient):
    url = django.urls.reverse("api-schema")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.headers["Content-Type"] == "application/json"
    assert response.data["info"]["title"] == "Eurydice origin API"
