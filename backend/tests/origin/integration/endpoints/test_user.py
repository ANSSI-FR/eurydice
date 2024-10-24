import django.urls
import freezegun
import pytest
from django.conf import settings
from django.utils import timezone
from faker import Faker
from rest_framework import status
from rest_framework import test
from rest_framework.authtoken.models import Token

from eurydice.common.api import serializers
from tests.origin.integration import factory


@pytest.mark.django_db()
class TestUser:
    def test_get_association_token(self, api_client: test.APIClient) -> None:
        user_profile = factory.UserProfileFactory()

        api_client.force_login(user=user_profile.user)
        url = django.urls.reverse("user-association")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert {"token", "expires_at"} == response.data.keys()

        serializer = serializers.AssociationTokenSerializer(data=response.data)
        assert serializer.is_valid()

        deserialized_token = serializer.validated_data
        assert deserialized_token.user_profile_id == user_profile.id

    def test_get_association_token_error_not_authenticated(
        self, api_client: test.APIClient
    ) -> None:
        url = django.urls.reverse("user-association")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"].code == "not_authenticated"

    def test_api_call_updates_user_last_access__remote_user(
        self,
        api_client: test.APIClient,
        faker: Faker,
    ):
        user = factory.UserFactory()
        api_client.credentials(**{settings.REMOTE_USER_HEADER: user.username})

        assert user.last_access is None

        url = django.urls.reverse("user-login")

        a_date = faker.date_time_this_decade(tzinfo=timezone.get_current_timezone())
        with freezegun.freeze_time(a_date):
            response = api_client.get(url)
            assert response.status_code == 204

        user.refresh_from_db()
        assert user.last_access == a_date

    def test_api_call_updates_user_last_access__token(
        self,
        api_client: test.APIClient,
        faker: Faker,
    ):
        user = factory.UserFactory()
        token = Token.objects.create(user=user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

        assert user.last_access is None

        url = django.urls.reverse("transferable-list")

        a_date = faker.date_time_this_decade(tzinfo=timezone.get_current_timezone())
        with freezegun.freeze_time(a_date):
            response = api_client.get(url)
            assert response.status_code == 200

        user.refresh_from_db()
        assert user.last_access == a_date
