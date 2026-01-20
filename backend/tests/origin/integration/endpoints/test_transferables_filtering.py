import hashlib
from datetime import datetime, timedelta

import freezegun
import pytest
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from faker import Faker
from rest_framework import status, test

from eurydice.origin.core import enums
from tests.origin.integration import factory


def _fdate(date: datetime) -> str:
    return date.isoformat()[:-6] + "Z"


@pytest.mark.django_db()
class TestOutgoingTransferableFiltering:
    def test_filter_creation_date(
        self,
        api_client: test.APIClient,
        faker: Faker,
    ):
        user_profile = factory.UserProfileFactory()

        a_date = faker.date_time_this_decade(tzinfo=timezone.get_current_timezone())
        ref_date = a_date + timedelta(days=2)

        for days in (0, 1, 3, 4):
            with freezegun.freeze_time(a_date + timedelta(days=days)):
                factory.OutgoingTransferableFactory(user_profile=user_profile)

        api_client.force_login(user_profile.user)
        url = reverse("transferable-list")
        response = api_client.get(url, {"created_after": _fdate(ref_date)})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2
        assert len(response.data["results"]) == 2

        for data in response.data["results"]:
            assert parse_datetime(data["created_at"]) > ref_date

        response = api_client.get(
            url,
            {
                "created_after": _fdate(ref_date),
                "page": response.data["pages"]["current"],
            },
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2
        assert len(response.data["results"]) == 2

    def test_filter_state(
        self,
        api_client: test.APIClient,
    ):
        user_profile = factory.UserProfileFactory()
        api_client.force_login(user_profile.user)

        for state in enums.TransferableRangeTransferState.names:
            factory.TransferableRangeFactory(
                transfer_state=state,
                outgoing_transferable=factory.OutgoingTransferableFactory(
                    user_profile=user_profile, _submission_succeeded=True
                ),
            )

        for state in ("PENDING", "ONGOING", "ERROR", "SUCCESS"):
            url = reverse("transferable-list")
            response = api_client.get(url, {"state": state})

            assert response.status_code == status.HTTP_200_OK
            assert response.data["count"] == 1
            assert len(response.data["results"]) == 1

            for data in response.data["results"]:
                assert data["state"] == state

    def test_filter_name(
        self,
        api_client: test.APIClient,
    ):
        user_profile = factory.UserProfileFactory()
        api_client.force_login(user_profile.user)

        for name in ("aaa.txt", "bbb.txt", "aaa.bin", "txt.aaa", "ccc.txt"):
            factory.OutgoingTransferableFactory(user_profile=user_profile, name=name)

        url = reverse("transferable-list")
        response = api_client.get(url, {"name": ".txt"})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 3
        assert len(response.data["results"]) == 3

        for data in response.data["results"]:
            assert data["name"].endswith(".txt")

    def test_filter_sha1(
        self,
        api_client: test.APIClient,
    ):
        user_profile = factory.UserProfileFactory()
        api_client.force_login(user_profile.user)

        for name in ("aaa.txt", "bbb.txt", "aaa.bin", "txt.aaa", "ccc.txt"):
            factory.OutgoingTransferableFactory(
                user_profile=user_profile,
                name=name,
                submission_succeeded_at=timezone.now(),
                sha1=hashlib.sha1(name.encode("utf-8")).digest(),
            )

        url = reverse("transferable-list")
        response = api_client.get(url, {"sha1": hashlib.sha1(b"txt.aaa").hexdigest()})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert len(response.data["results"]) == 1

        for data in response.data["results"]:
            assert data["name"] == "txt.aaa"

    def test_filter_submission_succeeded(
        self,
        api_client: test.APIClient,
        faker: Faker,
    ):
        user_profile = factory.UserProfileFactory()

        a_date = faker.date_time_this_decade(tzinfo=timezone.get_current_timezone())

        for days in (-6, -1, 2, 1):
            factory.OutgoingTransferableFactory(
                user_profile=user_profile,
                _submission_succeeded=True,
                _submission_succeeded_at=a_date + timedelta(days=days),
            )

        api_client.force_login(user_profile.user)
        url = reverse("transferable-list")
        response = api_client.get(url, {"submission_succeeded_before": _fdate(a_date)})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2
        assert len(response.data["results"]) == 2

        for data in response.data["results"]:
            assert parse_datetime(data["submission_succeeded_at"]) < a_date

    def test_filter_transfer_finished(
        self,
        api_client: test.APIClient,
        faker: Faker,
    ):
        user_profile = factory.UserProfileFactory()

        a_date = faker.date_time_this_decade(tzinfo=timezone.get_current_timezone())

        with freezegun.freeze_time(a_date + timedelta(days=-1000)):
            for days in (5, 2, -9, 1):
                factory.TransferableRangeFactory(
                    transfer_state=enums.TransferableRangeTransferState.TRANSFERRED,
                    size=42,
                    byte_offset=0,
                    finished_at=a_date + timedelta(days=days),
                    outgoing_transferable=factory.OutgoingTransferableFactory(
                        user_profile=user_profile, _submission_succeeded=True, size=42
                    ),
                )

        api_client.force_login(user_profile.user)
        url = reverse("transferable-list")
        response = api_client.get(url, {"transfer_finished_after": _fdate(a_date)})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 3
        assert len(response.data["results"]) == 3

        for data in response.data["results"]:
            assert parse_datetime(data["finished_at"]) > a_date

    def test_page_size(self, api_client: test.APIClient):
        user_profile = factory.UserProfileFactory()
        factory.OutgoingTransferableFactory.create_batch(55, user_profile=user_profile)

        api_client.force_login(user_profile.user)
        url = reverse("transferable-list")

        response = api_client.get(url, {"page_size": 25})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 55
        assert len(response.data["results"]) == 25

        response = api_client.get(url, {"page_size": 20})
        response = api_client.get(
            url,
            {"page_size": 20, "delta": 2, "from": response.data["pages"]["current"]},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 55
        assert len(response.data["results"]) == 15

    def test_isodate(
        self,
        api_client: test.APIClient,
        faker: Faker,
    ):
        user_profile = factory.UserProfileFactory()

        a_date = faker.date_time_this_decade(tzinfo=timezone.get_current_timezone())

        with freezegun.freeze_time(a_date):
            factory.OutgoingTransferableFactory(user_profile=user_profile)

        # check if the returned date is the exact creation date (same timezone)
        api_client.force_login(user_profile.user)
        url = reverse("transferable-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert len(response.data["results"]) == 1

        retrieved_str_date = response.data["results"][0]["created_at"]
        retrieved_date = parse_datetime(retrieved_str_date)

        assert a_date == retrieved_date

        # check if comparison with the same format than the input is OK : after
        api_client.force_login(user_profile.user)
        url = reverse("transferable-list")
        response = api_client.get(url, {"created_after": retrieved_str_date})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert len(response.data["results"]) == 1

        # check if comparison with the same format than the input is OK : before
        api_client.force_login(user_profile.user)
        url = reverse("transferable-list")
        response = api_client.get(url, {"created_before": retrieved_str_date})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert len(response.data["results"]) == 1
