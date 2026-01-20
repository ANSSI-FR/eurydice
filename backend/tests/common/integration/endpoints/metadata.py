from django.urls import reverse
from rest_framework import status, test

from eurydice.common.config.settings.test import EURYDICE_CONTACT_FR, UI_BADGE_COLOR, UI_BADGE_CONTENT


def metadata(api_client: test.APIClient):
    url = reverse("server-metadata")

    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK, response.status_code
    assert response.data["contact"] == EURYDICE_CONTACT_FR
    assert response.data["badge_content"] == UI_BADGE_CONTENT
    assert response.data["badge_color"] == UI_BADGE_COLOR
    assert not response.data["encryption_enabled"]

    return response
