from unittest import mock

import django.urls
import humanfriendly as hf
import pytest
from django import conf
from django.contrib import auth
from django.utils import timezone
from faker import Faker
from rest_framework import status
from rest_framework import test

from eurydice.common.api import serializers
from eurydice.destination.core import models
from tests.common.integration import factory as common_factory
from tests.destination.integration import factory


@pytest.mark.django_db()
class TestUser:
    def test_post_association_token_success_no_user_profile(
        self, settings: conf.Settings, api_client: test.APIClient
    ):
        settings.USER_ASSOCIATION_TOKEN_EXPIRES_AFTER = hf.parse_timespan("1h")
        token = common_factory.AssociationTokenFactory()

        payload = serializers.AssociationTokenSerializer(token).data

        user = factory.UserFactory()
        assert auth.get_user_model().objects.get() == user
        assert (
            auth.get_user_model()
            .objects.filter(id=user.id, user_profile__isnull=True)
            .exists()
        )
        assert not models.UserProfile.objects.exists()

        api_client.force_login(user=user)
        url = django.urls.reverse("user-association")
        response = api_client.post(url, data=payload, format="json")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert auth.get_user_model().objects.get() == user
        assert models.UserProfile.objects.get(
            user=user.id, associated_user_profile_id=token.user_profile_id
        )

    def test_post_association_token_success_existing_user_profile(
        self, settings: conf.Settings, api_client: test.APIClient
    ):
        user = factory.UserFactory()
        settings.USER_ASSOCIATION_TOKEN_EXPIRES_AFTER = hf.parse_timespan("1h")
        token = common_factory.AssociationTokenFactory()

        factory.UserProfileFactory(
            user=None, associated_user_profile_id=token.user_profile_id
        )

        payload = serializers.AssociationTokenSerializer(token).data
        api_client.force_login(user=user)
        url = django.urls.reverse("user-association")
        response = api_client.post(url, data=payload, format="json")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert models.UserProfile.objects.get(
            user=user.id, associated_user_profile_id=token.user_profile_id
        )

    def test_post_association_token_error_not_authenticated(
        self, api_client: test.APIClient
    ):
        url = django.urls.reverse("user-association")
        response = api_client.post(url, data={}, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"].code == "not_authenticated"

    def test_post_association_token_error_non_readable_token(
        self, api_client: test.APIClient
    ):
        user = factory.UserFactory()
        assert not models.UserProfile.objects.exists()

        api_client.force_login(user=user)
        url = django.urls.reverse("user-association")
        response = api_client.post(url, data={"token": "foo bar baz"}, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["token"].code == "invalid"
        assert str(response.data["token"]) == "Malformed token."
        assert not models.UserProfile.objects.exists()

    def test_post_association_token_error_invalid_token_signature(
        self, settings: conf.Settings, api_client: test.APIClient
    ):
        settings.USER_ASSOCIATION_TOKEN_SECRET_KEY = (
            "kzuzabvqkcc8b4frle16pptynbrlyo6pmfvx"
        )
        settings.USER_ASSOCIATION_TOKEN_EXPIRES_AFTER = hf.parse_timespan("1h")

        forged_token = common_factory.AssociationTokenFactory()
        payload = serializers.AssociationTokenSerializer(forged_token).data

        user = factory.UserFactory()
        assert not models.UserProfile.objects.exists()

        settings.USER_ASSOCIATION_TOKEN_SECRET_KEY = "0" * 36

        api_client.force_login(user=user)
        url = django.urls.reverse("user-association")
        response = api_client.post(url, data=payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["token"].code == "invalid"
        assert str(response.data["token"]) == "Invalid association token signature."
        assert not models.UserProfile.objects.exists()

    def test_post_association_token_error_expired_token(
        self, faker: Faker, api_client: test.APIClient
    ):
        token = common_factory.AssociationTokenFactory(
            expires_at=faker.date_time_this_decade(
                tzinfo=timezone.get_current_timezone()
            )
        )
        token.verify_validity_time = mock.Mock()
        payload = serializers.AssociationTokenSerializer(token).data

        user = factory.UserFactory()
        assert not models.UserProfile.objects.exists()

        api_client.force_login(user=user)
        url = django.urls.reverse("user-association")
        response = api_client.post(url, data=payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["token"].code == "invalid"
        assert str(response.data["token"]) == "The association token has expired."
        assert not models.UserProfile.objects.exists()

    def test_post_association_token_error_already_associated(
        self, settings: conf.Settings, api_client: test.APIClient
    ):
        user_profile = factory.UserProfileFactory()

        settings.USER_ASSOCIATION_TOKEN_EXPIRES_AFTER = hf.parse_timespan("1h")
        token = common_factory.AssociationTokenFactory()

        payload = serializers.AssociationTokenSerializer(token).data

        assert models.UserProfile.objects.get() == user_profile

        api_client.force_login(user=user_profile.user)
        url = django.urls.reverse("user-association")
        response = api_client.post(url, data=payload, format="json")

        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.data["detail"].code == "AlreadyAssociatedError"
        assert (
            str(response.data["detail"])
            == "The user is already associated with a user from the origin side."
        )
        assert models.UserProfile.objects.get() == user_profile

    def test_post_association_token_error_profile_already_associated(
        self, settings: conf.Settings, api_client: test.APIClient
    ):
        settings.USER_ASSOCIATION_TOKEN_EXPIRES_AFTER = hf.parse_timespan("1h")
        token = common_factory.AssociationTokenFactory()

        factory.UserProfileFactory(
            user=None, associated_user_profile_id=token.user_profile_id
        )

        payload = serializers.AssociationTokenSerializer(token).data

        url = django.urls.reverse("user-association")

        user = factory.UserFactory()
        api_client.force_login(user=user)
        response = api_client.post(url, data=payload, format="json")

        assert response.status_code == status.HTTP_204_NO_CONTENT

        other_user = factory.UserFactory()
        api_client.force_login(user=other_user)
        response = api_client.post(url, data=payload, format="json")

        assert response.status_code == status.HTTP_409_CONFLICT
