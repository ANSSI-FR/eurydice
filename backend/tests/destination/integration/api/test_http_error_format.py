from unittest import mock

import django.urls
import pytest
from rest_framework import exceptions, test

from eurydice.destination.api.views.user_association import UserAssociationView
from tests.destination.integration import factory


@pytest.mark.django_db()
@pytest.mark.parametrize("exception", [exceptions.APIException, exceptions.ParseError])
def test_association_token_error_is_json(exception: exceptions.APIException, api_client: test.APIClient):
    """Tests that APIExceptions for HTTP errors 500 and 400 correctly return
    a JSON formatted error.

    NOTE: we test this only for this specific endpoint as it should behave the
            same regardless of which endpoint returns an HTTP error 500 and 400
    """
    user_profile = factory.UserProfileFactory()

    api_client.force_login(user=user_profile.user)

    url = django.urls.reverse("user-association")

    with mock.patch.object(UserAssociationView, "post", side_effect=exception):
        response = api_client.post(url)

    assert response.status_code == exception.status_code
    assert response.headers["Content-Type"] == "application/json"
