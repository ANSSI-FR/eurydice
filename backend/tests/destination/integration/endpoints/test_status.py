import dateutil
import freezegun
import pytest
from django.urls import reverse
from django.utils import timezone
from faker import Faker
from rest_framework import test

from eurydice.destination.api.views import StatusView
from eurydice.destination.core.models import LastPacketReceivedAt
from tests.destination.integration import factory


@pytest.mark.django_db()
def test_get_status(
    faker: Faker,
    api_client: test.APIClient,
):
    # Test preparation
    LastPacketReceivedAt.update()

    timestamp = faker.date_time_this_decade(tzinfo=timezone.get_current_timezone())
    with freezegun.freeze_time(timestamp):
        LastPacketReceivedAt.update()

    user_profile = factory.UserProfileFactory()
    api_client.force_authenticate(user_profile.user)

    # Actual test
    assert StatusView.get_object(None) == {"last_packet_received_at": timestamp}

    url = reverse("status")
    response = api_client.get(url)
    response_json = response.json()
    assert len(response_json) == 1
    assert dateutil.parser.parse(response_json["last_packet_received_at"]) == timestamp
