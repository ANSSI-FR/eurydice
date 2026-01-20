from datetime import datetime, timedelta

import dateutil
import freezegun
import pytest
from django import conf
from django.contrib.auth.models import Permission
from django.db.models import Q, Sum
from django.urls import reverse
from django.utils import timezone
from faker import Faker
from rest_framework import test

from eurydice.common.enums import OutgoingTransferableState as States
from eurydice.origin.api.views import metrics
from eurydice.origin.core.enums import TransferableRangeTransferState
from eurydice.origin.core.models import LastPacketSentAt
from eurydice.origin.core.models.outgoing_transferable import OutgoingTransferable
from eurydice.origin.core.models.transferable_range import TransferableRange
from tests.origin.integration import factory


def create_transferable(state: States, date: datetime) -> OutgoingTransferable:
    with freezegun.freeze_time(date):
        kwargs = {
            "make_transferable_ranges_for_state": state,
        }
        if state == States.SUCCESS:
            kwargs["_submission_succeeded"] = True
            kwargs["make_transferable_ranges_for_state__finished_at"] = date
        else:
            kwargs["_submission_succeeded"] = False
        return factory.OutgoingTransferableFactory(**kwargs)


def sum_pending_transferable_ranges_size(
    outgoing_transferable: OutgoingTransferable,
) -> int:
    return TransferableRange.objects.aggregate(
        value=Sum(
            "size",
            filter=Q(
                outgoing_transferable=outgoing_transferable,
                transfer_state=TransferableRangeTransferState.PENDING,
            ),
        )
    )["value"]


@pytest.mark.django_db()
@pytest.mark.parametrize(
    (
        "old_states_repetitions",
        "recent_states_repetitions",
    ),
    [
        ([2, 4, 6, 8, 10], [1, 3, 5, 7, 9]),
        ([0, 0, 0, 0, 0], [0, 0, 0, 0, 0]),
        ([0, 2, 0, 2, 0], [0, 2, 0, 2, 0]),
        ([2, 0, 2, 0, 2], [2, 0, 2, 0, 2]),
        ([1, 0, 4, 2, 0], [0, 4, 2, 0, 1]),
    ],
)
def test__generate_metrics(
    faker: Faker,
    settings: conf.Settings,
    api_client: test.APIClient,
    old_states_repetitions: list[int],
    recent_states_repetitions: list[int],
) -> None:
    # Test preparation

    # We make sure the parameterization is consistent with the amount of
    # known states. We use this data structure in parameterization because it
    # is more concise (and readable) than a Dict[States, int]
    assert len(old_states_repetitions) == len(States.values)
    assert len(recent_states_repetitions) == len(States.values)

    old_transferable_nb = {
        States.PENDING: old_states_repetitions[0],
        States.ONGOING: old_states_repetitions[1],
        States.ERROR: old_states_repetitions[2],
        States.CANCELED: old_states_repetitions[3],
        States.SUCCESS: old_states_repetitions[4],
    }

    recent_transferable_nb = {
        States.PENDING: recent_states_repetitions[0],
        States.ONGOING: recent_states_repetitions[1],
        States.ERROR: recent_states_repetitions[2],
        States.CANCELED: recent_states_repetitions[3],
        States.SUCCESS: recent_states_repetitions[4],
    }

    settings.METRICS_SLIDING_WINDOW = 3600

    # With the current fixed faker seed, faker just happens to return a datetime
    # within 4000 seconds of a "spring forward", due to daylight saving time,
    # which means that while the following code passes the test, it would fail
    # if recent_date was using the fake datetime
    # and old_date was computed using recent_date - 4000 seconds.
    old_date = faker.date_time_this_decade(tzinfo=timezone.get_current_timezone())
    recent_date = old_date + timedelta(seconds=4000)

    expected = {
        "queue_size": 0,
    }

    for state, repetitions in old_transferable_nb.items():
        for _ in range(repetitions):
            old_transferable = create_transferable(state=state, date=old_date)

            if state == States.ONGOING:
                expected["queue_size"] += sum_pending_transferable_ranges_size(old_transferable)

    for state, repetitions in recent_transferable_nb.items():
        for _ in range(repetitions):
            recent_transferable = create_transferable(state=state, date=recent_date)

            if state == States.ONGOING:
                expected["queue_size"] += sum_pending_transferable_ranges_size(recent_transferable)

    expected["pending_transferables"] = old_transferable_nb[States.PENDING] + recent_transferable_nb[States.PENDING]
    expected["ongoing_transferables"] = old_transferable_nb[States.ONGOING] + recent_transferable_nb[States.ONGOING]
    expected["recent_successes"] = recent_transferable_nb[States.SUCCESS]
    expected["recent_errors"] = recent_transferable_nb[States.ERROR]
    expected["last_packet_sent_at"] = None

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
def test__last_packet_sent_at(
    faker: Faker,
    api_client: test.APIClient,
):
    # Test preparation
    LastPacketSentAt.update()

    timestamp = faker.date_time_this_decade(tzinfo=timezone.get_current_timezone())
    with freezegun.freeze_time(timestamp):
        LastPacketSentAt.update()

    user_profile = factory.UserProfileFactory()
    permission = Permission.objects.get(codename="view_rolling_metrics")
    user_profile.user.user_permissions.add(permission)
    api_client.force_authenticate(user_profile.user)

    # Actual test
    url = reverse("metrics")
    response = api_client.get(url)
    response_json = response.json()
    assert dateutil.parser.parse(response_json["last_packet_sent_at"]) == timestamp


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
