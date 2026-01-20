from datetime import datetime, timedelta

import dateutil
import freezegun
import pytest
from django import conf
from django.contrib.auth.models import Permission
from django.urls import reverse
from django.utils import timezone
from faker import Faker
from rest_framework import test

from eurydice.destination.api.views import metrics
from eurydice.destination.core.models import IncomingTransferable, LastPacketReceivedAt
from eurydice.destination.core.models import IncomingTransferableState as States
from tests.destination.integration import factory


def create_transferable(state: States, date: datetime) -> IncomingTransferable:
    with freezegun.freeze_time(date):
        return factory.IncomingTransferableFactory(
            state=state,
            _finished_at=date,
        )


@pytest.mark.django_db()
@pytest.mark.parametrize(
    (
        "old_states_repetitions",
        "recent_states_repetitions",
    ),
    [
        ([2, 4, 6, 8, 10, 12], [1, 3, 5, 7, 9, 11]),
        ([0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]),
        ([0, 2, 0, 2, 0, 2], [0, 2, 0, 2, 0, 2]),
        ([2, 0, 2, 0, 2, 0], [2, 0, 2, 0, 2, 0]),
        ([1, 0, 4, 2, 0, 1], [0, 4, 2, 0, 1, 1]),
    ],
)
def test__generate_metrics(
    faker: Faker,
    settings: conf.Settings,
    api_client: test.APIClient,
    old_states_repetitions: list[int],
    recent_states_repetitions: list[int],
):
    # Test preparation

    # We make sure the parameterization is consistent with the amount of
    # known states. We use this data structure in parameterization because it
    # is more concise (and readable) than a Dict[States, int]
    assert len(old_states_repetitions) == len(States.values)
    assert len(recent_states_repetitions) == len(States.values)

    old_transferable_nb = {
        States.ONGOING: old_states_repetitions[0],
        States.SUCCESS: old_states_repetitions[1],
        States.ERROR: old_states_repetitions[2],
        States.REVOKED: old_states_repetitions[3],
        States.EXPIRED: old_states_repetitions[4],
        States.REMOVED: old_states_repetitions[5],
    }

    recent_transferable_nb = {
        States.ONGOING: recent_states_repetitions[0],
        States.SUCCESS: recent_states_repetitions[1],
        States.ERROR: recent_states_repetitions[2],
        States.REVOKED: recent_states_repetitions[3],
        States.EXPIRED: recent_states_repetitions[4],
        States.REMOVED: recent_states_repetitions[5],
    }

    settings.METRICS_SLIDING_WINDOW = 3600

    # With the current fixed faker seed, faker just happens to return a datetime
    # within 4000 seconds of a "spring forward", due to daylight saving time,
    # which means that while the following code passes the test, it would fail
    # if recent_date was using the fake datetime
    # and old_date was computed using recent_date - 4000 seconds.
    old_date = faker.date_time_this_decade(tzinfo=timezone.get_current_timezone())
    recent_date = old_date + timedelta(seconds=4000)

    for state, repetitions in old_transferable_nb.items():
        for _ in range(repetitions):
            create_transferable(state=state, date=old_date)

    for state, repetitions in recent_transferable_nb.items():
        for _ in range(repetitions):
            create_transferable(state=state, date=recent_date)

    expected = {
        "ongoing_transferables": (old_transferable_nb[States.ONGOING] + recent_transferable_nb[States.ONGOING]),
        "recent_successes": (
            recent_transferable_nb[States.SUCCESS]
            + recent_transferable_nb[States.EXPIRED]
            + recent_transferable_nb[States.REMOVED]
        ),
        "recent_errors": recent_transferable_nb[States.ERROR],
        "last_packet_received_at": None,
    }

    # Actual test
    user_profile = factory.UserProfileFactory()
    permission = Permission.objects.get(codename="view_rolling_metrics")
    user_profile.user.user_permissions.add(permission)

    with freezegun.freeze_time(recent_date):
        assert metrics.MetricsView.get_object(None) == expected

        api_client.force_authenticate(user_profile.user)
        url = reverse("metrics")
        response = api_client.get(url)
        assert response.json() == expected


@pytest.mark.django_db()
def test__last_packet_received_at(
    faker: Faker,
    api_client: test.APIClient,
):
    # Test preparation
    LastPacketReceivedAt.update()

    timestamp = faker.date_time_this_decade(tzinfo=timezone.get_current_timezone())
    with freezegun.freeze_time(timestamp):
        LastPacketReceivedAt.update()

    user_profile = factory.UserProfileFactory()
    permission = Permission.objects.get(codename="view_rolling_metrics")
    user_profile.user.user_permissions.add(permission)
    api_client.force_authenticate(user_profile.user)

    # Actual test
    url = reverse("metrics")
    response = api_client.get(url)
    response_json = response.json()
    assert dateutil.parser.parse(response_json["last_packet_received_at"]) == timestamp


@pytest.mark.django_db()
def test__metrics_permissions_deny(api_client: test.APIClient):
    user_profile = factory.UserProfileFactory()
    url = reverse("metrics")

    response = api_client.get(url)

    assert response.status_code == 401

    api_client.force_authenticate(user_profile.user)
    response = api_client.get(url)

    assert response.status_code == 403
    assert "You do not have permission" in response.json()["detail"]


@pytest.mark.django_db()
def test__metrics_permissions_allow(api_client: test.APIClient):
    user_profile = factory.UserProfileFactory()
    permission = Permission.objects.get(codename="view_rolling_metrics")
    user_profile.user.user_permissions.add(permission)

    api_client.force_authenticate(user_profile.user)
    url = reverse("metrics")
    response = api_client.get(url)

    assert response.status_code == 200
