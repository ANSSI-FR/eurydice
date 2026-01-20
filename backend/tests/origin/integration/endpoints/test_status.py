import dateutil
import freezegun
import pytest
from django.urls import reverse
from django.utils import timezone
from faker import Faker
from rest_framework import status, test

from eurydice.origin.core import models
from tests.origin.integration import factory


@pytest.mark.django_db()
def test_get_metrics_permissions_deny(api_client: test.APIClient):
    url = reverse("metrics")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db()
def test_get_status__no_maintenance_no_packet_sent(
    api_client: test.APIClient,
) -> None:
    user_profile = factory.UserProfileFactory()
    api_client.force_authenticate(user_profile.user)

    url = reverse("status")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "maintenance": False,
        "last_packet_sent_at": None,
    }


@pytest.mark.django_db()
def test_get_status__maintenance_with_packet_timestamp(
    faker: Faker,
    api_client: test.APIClient,
) -> None:
    maintenance = models.Maintenance.objects.get()
    maintenance.maintenance = True
    maintenance.save()

    timestamp = faker.date_time_this_decade(tzinfo=timezone.get_current_timezone())
    with freezegun.freeze_time(timestamp):
        models.LastPacketSentAt.update()

    user_profile = factory.UserProfileFactory()
    api_client.force_authenticate(user_profile.user)

    url = reverse("status")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert len(response_json) == 2
    assert response_json["maintenance"] is True
    assert dateutil.parser.parse(response_json["last_packet_sent_at"]) == timestamp


@pytest.mark.django_db()
def test_get_status_permissions_deny(
    api_client: test.APIClient,
) -> None:
    url = reverse("status")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
