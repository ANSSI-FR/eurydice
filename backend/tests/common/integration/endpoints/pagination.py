from typing import Any, Callable
from uuid import UUID

import pytest
from django.db import transaction
from django.urls import reverse
from rest_framework import status, test
from rest_framework.response import Response
from rest_framework.settings import api_settings

from eurydice.common.api.pagination import EurydiceSessionPagination

PAGES = 5
PAGE_SIZE = 12


class PaginationTestsInTransactionSuperclass(test.APITransactionTestCase):
    def create_transferables(self) -> None:
        """Initialize database with SUCCESSful and ERRORed transferables."""

        assert PAGES >= 5
        assert PAGE_SIZE % 2 == 0
        assert PAGE_SIZE % 3 == 0
        assert PAGE_SIZE * PAGES > api_settings.PAGE_SIZE

        with transaction.atomic():
            self.user_profile = type(self).user_profile_factory()
            type(self).make_transferables(
                PAGES * PAGE_SIZE // 2,
                user_profile=self.user_profile,
                state=self.success_state,
            )
            type(self).make_transferables(
                PAGES * PAGE_SIZE // 2,
                user_profile=self.user_profile,
                state=self.success_state,
            )

    def list_transferables(self, **parameters) -> Response:
        url = reverse("transferable-list")

        if "from_" in parameters:
            parameters["from"] = parameters.pop("from_")
        return self.client.get(url, parameters)

    def expected_ids(self) -> list[str]:
        """Read the IDs we're going to paginate through, right from the database."""

        return [
            str(elm)
            for elm in type(self).transferable_class.objects.order_by("-created_at").values_list("id", flat=True)
        ]

    def success_ids(self) -> list[str]:
        """Read the IDs of Transferables in SUCCESS state."""

        return [
            str(elm)
            for elm in type(self)
            .transferable_class.objects.filter(state=type(self).success_state.SUCCESS)
            .order_by("-created_at")
            .values_list("id", flat=True)
        ]

    def trim_transferables(self, count: int) -> None:
        """Delete the requested amount of transferables to emulate a DBTrimmer."""

        type(self).transferable_class.objects.filter(
            id__in=type(self).transferable_class.objects.order_by("created_at").values_list("id")[:count]
        ).delete()

    def insert_decoy_transferables(self, count: int = 2) -> None:
        """Add the requested amount of *new* transferables in the database."""

        type(self).make_transferables(
            count,
            user_profile=type(self).transferable_class.objects.first().user_profile,
        )

    def assert_slice(
        self,
        response: Response,
        expected_ids: list[str],
        start: int,
        end: int,
        page: int | None = None,
        count: int | None = None,
    ):
        """Make sure the API response matches the expected data slice."""

        assert response.status_code == status.HTTP_200_OK
        assert response.data["offset"] == start
        assert response.data["count"] == len(expected_ids) if count is None else count
        data = response.data["results"]
        assert len(data) == end - start
        for i in range(start, end):
            assert data[i - start]["id"] == expected_ids[i]

    def setUp(self):
        self.create_transferables()
        self.client.force_authenticate(self.user_profile.user)

    def test_forward_ending(
        self,
    ):
        TOTAL = PAGES * PAGE_SIZE  # noqa: N806
        EXPECTED_LAST_PAGE_SIZE = 2  # noqa: N806
        TOTAL_WITHOUT_EXPECTED_LAST_PAGE = TOTAL - EXPECTED_LAST_PAGE_SIZE  # noqa: N806
        TEST_PAGE_SIZE = int(  # noqa: N806
            (TOTAL_WITHOUT_EXPECTED_LAST_PAGE) / (PAGES - 1)
        )
        TEST_FULL_PAGES = int(TOTAL / TEST_PAGE_SIZE)  # noqa: N806
        TEST_LAST_PAGE_SIZE = TOTAL - TEST_FULL_PAGES * TEST_PAGE_SIZE  # noqa: N806

        assert 0 < TEST_LAST_PAGE_SIZE < TEST_PAGE_SIZE

        expected_ids = self.expected_ids()

        response = self.list_transferables(page_size=TEST_PAGE_SIZE)
        first = response.data["pages"]["current"]
        response = self.list_transferables(page_size=TEST_PAGE_SIZE, delta=TEST_FULL_PAGES, from_=first)
        last_page = response.data["pages"]["current"]
        assert response.data["pages"]["next"] is None
        self.assert_slice(
            response,
            expected_ids,
            TEST_PAGE_SIZE * TEST_FULL_PAGES,
            TOTAL,
        )

        self.insert_decoy_transferables()

        response = self.list_transferables(page_size=TEST_PAGE_SIZE, page=last_page)
        assert response.data["pages"]["next"] is None
        self.assert_slice(
            response,
            expected_ids,
            TEST_PAGE_SIZE * TEST_FULL_PAGES,
            TOTAL,
        )

        response = self.list_transferables(page_size=TEST_PAGE_SIZE, delta=1, from_=last_page)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_reverse_ending(
        self,
    ):
        response = self.list_transferables(page_size=PAGE_SIZE)
        assert response.data["pages"]["previous"] is None
        current = response.data["pages"]["current"]
        self.assert_slice(response, self.expected_ids(), 0, PAGE_SIZE)

        self.insert_decoy_transferables()

        response = self.list_transferables(page_size=PAGE_SIZE, delta=-1, from_=current)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_dbtrimmer_with_cursor_changed_pages(
        self,
    ):
        expected_ids = self.expected_ids()

        response = self.list_transferables(page_size=PAGE_SIZE)
        first_page = response.data["pages"]["current"]
        response = self.list_transferables(page_size=PAGE_SIZE, delta=PAGES - 1, from_=first_page)
        current = response.data["pages"]["current"]
        self.assert_slice(response, expected_ids, PAGE_SIZE * (PAGES - 1), PAGE_SIZE * PAGES)

        self.trim_transferables(PAGE_SIZE // 2)

        response = self.list_transferables(page_size=PAGE_SIZE, page=current)
        current = response.data["pages"]["current"]
        self.assert_slice(
            response,
            expected_ids,
            PAGE_SIZE * (PAGES - 1),
            PAGE_SIZE * (PAGES - 1) + PAGE_SIZE // 2,
            count=PAGE_SIZE * (PAGES - 1) + PAGE_SIZE // 2,
        )

        self.trim_transferables(PAGE_SIZE // 2 + 2)

        self.insert_decoy_transferables(PAGE_SIZE // 3)

        # The last page disappeared
        response = self.list_transferables(page_size=PAGE_SIZE, page=current)
        assert response.status_code == status.HTTP_410_GONE

        # The second to last page is now the last one, with 2 transferables less
        response = self.list_transferables(page_size=PAGE_SIZE, delta=-1, from_=current)
        self.assert_slice(
            response,
            expected_ids,
            PAGE_SIZE * (PAGES - 2),
            PAGE_SIZE * (PAGES - 1) - 2,
            count=PAGE_SIZE * (PAGES - 1) - 2,
        )

    def test_almost_empty_database(
        self,
    ):
        expected_ids = self.expected_ids()

        self.trim_transferables(PAGE_SIZE * PAGES - PAGE_SIZE // 2)

        response = self.list_transferables(page_size=PAGE_SIZE)
        current = response.data["pages"]["current"]
        self.assert_slice(response, expected_ids, 0, PAGE_SIZE // 2, count=PAGE_SIZE // 2)

        response = self.list_transferables(page_size=PAGE_SIZE, page=current)
        self.assert_slice(response, expected_ids, 0, PAGE_SIZE // 2, count=PAGE_SIZE // 2)

        self.insert_decoy_transferables(2)
        self.trim_transferables(PAGE_SIZE // 2)  # Only 2 decoy transferables remaining

        response = self.list_transferables(page_size=PAGE_SIZE, page=current)
        assert response.status_code == status.HTTP_410_GONE

        response = self.list_transferables(page_size=PAGE_SIZE)
        current = response.data["pages"]["current"]
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2

        self.insert_decoy_transferables(2)

        response = self.list_transferables(page_size=PAGE_SIZE, page=current)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2

    def test_empty_database(
        self,
    ):
        expected_ids = self.expected_ids()
        self.trim_transferables(PAGE_SIZE * PAGES - PAGE_SIZE // 2)

        response = self.list_transferables(page_size=PAGE_SIZE)
        assert response.data["pages"]["previous"] is None
        current = response.data["pages"]["current"]
        self.assert_slice(response, expected_ids, 0, PAGE_SIZE // 2, count=PAGE_SIZE // 2)

        self.trim_transferables(PAGE_SIZE // 2)  # Nothing left in the DB

        response = self.list_transferables(page_size=PAGE_SIZE)
        assert response.data["pages"]["previous"] is None
        assert response.data["pages"]["current"] is None
        assert response.data["pages"]["next"] is None
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0
        assert len(response.data["results"]) == 0

        response = self.list_transferables(page_size=PAGE_SIZE, page=current)
        assert response.status_code == status.HTTP_410_GONE

    def test_empty_database_edge_cases(
        self,
    ):
        expected_ids = self.expected_ids()
        self.trim_transferables(PAGE_SIZE * (PAGES - 1) - 1)

        response = self.list_transferables(page_size=PAGE_SIZE)
        next_page = response.data["pages"]["next"]
        response = self.list_transferables(page_size=PAGE_SIZE, page=next_page)
        previous = response.data["pages"]["previous"]
        current = response.data["pages"]["current"]
        self.assert_slice(
            response,
            expected_ids,
            PAGE_SIZE,
            PAGE_SIZE + 1,
            count=PAGE_SIZE + 1,
        )

        self.trim_transferables(PAGE_SIZE)  # 1 transferable left in the DB after this line

        response = self.list_transferables(page_size=PAGE_SIZE, page=current)
        assert response.status_code == status.HTTP_410_GONE

        self.insert_decoy_transferables(2)

        response = self.list_transferables(page_size=PAGE_SIZE, page=previous)
        self.assert_slice(response, expected_ids, 0, 1, count=1)

        response = self.list_transferables(page_size=PAGE_SIZE, delta=-1, from_=current)
        self.assert_slice(response, expected_ids, 0, 1, count=1)

        self.trim_transferables(1)  # Only decoys in the DB

        response = self.list_transferables(page_size=PAGE_SIZE, page=previous)
        assert response.status_code == status.HTTP_410_GONE

        self.trim_transferables(2)  # Nothing left in the DB

        response = self.list_transferables(page_size=PAGE_SIZE, delta=-1, from_=current)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_additional_query_params(
        self,
    ):
        expected_ids = self.success_ids()

        response = self.list_transferables(page_size=PAGE_SIZE // 3, state="SUCCESS")
        self.assert_slice(response, expected_ids, 0, PAGE_SIZE // 3)
        current = response.data["pages"]["current"]

        response = self.list_transferables(state="SUCCESS", page_size=PAGE_SIZE // 3, delta=1, from_=current)
        self.assert_slice(response, expected_ids, PAGE_SIZE // 3, 2 * PAGE_SIZE // 3)
        current = response.data["pages"]["current"]

        # Removing filters is not allowed
        response = self.list_transferables(page_size=PAGE_SIZE // 3, page=current)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # Changing page size on the fly is not allowed
        response = self.list_transferables(state="SUCCESS", page_size=PAGE_SIZE // 2, page=current)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_invalid_page(self):
        response = self.list_transferables(page_size=PAGE_SIZE * 2, page="billmurray")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_invalid_page_delta(
        self,
    ):
        response = self.list_transferables(page_size=PAGE_SIZE)
        current = response.data["pages"]["current"]
        self.assert_slice(response, self.expected_ids(), 0, PAGE_SIZE)

        response = self.list_transferables(page_size=PAGE_SIZE, delta=0, page=current)
        self.assert_slice(response, self.expected_ids(), 0, PAGE_SIZE)

        response = self.list_transferables(page_size=PAGE_SIZE, delta="hey", page=current)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_both_page_and_from(
        self,
    ):
        response = self.list_transferables(page_size=PAGE_SIZE)
        next_page = response.data["pages"]["next"]
        current = response.data["pages"]["current"]
        self.assert_slice(response, self.expected_ids(), 0, PAGE_SIZE)

        response = self.list_transferables(page_size=PAGE_SIZE, delta=1, page=next_page, from_=current)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_page_delta_without_from(
        self,
    ):
        response = self.list_transferables(page_size=PAGE_SIZE, delta=2)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class PaginationTestsSuperclass:
    @pytest.fixture(scope="class")
    def list_transferables(self, django_db_setup: None, django_db_blocker: Any) -> None:
        """Initialize database and return a lambda to query it."""

        assert PAGES >= 5
        assert PAGE_SIZE % 2 == 0
        assert PAGE_SIZE % 3 == 0
        assert PAGE_SIZE * PAGES > api_settings.PAGE_SIZE

        with django_db_blocker.unblock(), transaction.atomic():
            user_profile = type(self).user_profile_factory()
            type(self).make_transferables(
                PAGES * PAGE_SIZE // 2,
                user_profile=user_profile,
                state=self.success_state,
            )
            type(self).make_transferables(
                PAGES * PAGE_SIZE // 2,
                user_profile=user_profile,
                state=self.error_state,
            )
            api_client = test.APIClient()
            # don't use force_login here as it attempts to create a session in DB
            # and the atomic transaction block prevents other db queries
            api_client.force_authenticate(user_profile.user)
            url = reverse("transferable-list")

            def list_func(**parameters):
                if "from_" in parameters:
                    parameters["from"] = parameters.pop("from_")
                return api_client.get(url, parameters)

            yield list_func
            transaction.set_rollback(True)

    @pytest.fixture(scope="class")
    def expected_ids(self, list_transferables: Callable) -> list[str]:
        """Read the IDs we're going to paginate through, right from the database."""

        return [
            str(elm)
            for elm in type(self).transferable_class.objects.order_by("-created_at").values_list("id", flat=True)
        ]

    @pytest.fixture(scope="class")
    def success_ids(self, list_transferables: Callable) -> list[str]:
        """Read the IDs of Transferables in SUCCESS state."""

        return [
            str(elm)
            for elm in type(self)
            .transferable_class.objects.filter(state=type(self).success_state.SUCCESS)
            .order_by("-created_at")
            .values_list("id", flat=True)
        ]

    def trim_transferables(self, count: int) -> None:
        """Delete the requested amount of transferables to emulate a DBTrimmer."""

        type(self).transferable_class.objects.filter(
            id__in=type(self).transferable_class.objects.order_by("created_at").values_list("id")[:count]
        ).delete()

    def insert_decoy_transferables(self, count: int = 2) -> None:
        """Add the requested amount of *new* transferables in the database."""

        type(self).make_transferables(
            count,
            user_profile=type(self).transferable_class.objects.first().user_profile,
        )

    def assert_slice(
        self,
        response: Response,
        expected_ids: list[str],
        start: int,
        end: int,
        page: int | None = None,
        count: int | None = None,
    ):
        """Make sure the API response matches the expected data slice."""

        assert response.status_code == status.HTTP_200_OK
        assert response.data["offset"] == start
        assert response.data["count"] == len(expected_ids) if count is None else count
        data = response.data["results"]
        assert len(data) == end - start
        for i in range(start, end):
            assert data[i - start]["id"] == expected_ids[i]

    @pytest.mark.django_db()
    def test_page_size(self, list_transferables: Callable, expected_ids: list[UUID]):
        response = list_transferables(page_size=PAGE_SIZE // 2)
        self.assert_slice(response, expected_ids, 0, PAGE_SIZE // 2)

        response = list_transferables(page_size=PAGE_SIZE // 3)
        next_page = response.data["pages"]["next"]
        response = list_transferables(page_size=PAGE_SIZE // 3, page=next_page)
        self.assert_slice(response, expected_ids, PAGE_SIZE // 3, 2 * PAGE_SIZE // 3)

    @pytest.mark.django_db()
    def test_full_listing_without_delta(self, list_transferables: Callable, expected_ids: list[UUID]):
        response = list_transferables(page_size=PAGE_SIZE)
        next_page = response.data["pages"]["next"]
        paginated_at = response.data["paginated_at"]

        self.assert_slice(response, expected_ids, 0, PAGE_SIZE)

        for page in range(1, PAGES):
            response = list_transferables(page_size=PAGE_SIZE, page=next_page)
            next_page = response.data["pages"]["next"]
            assert paginated_at == response.data["paginated_at"]
            self.assert_slice(response, expected_ids, page * PAGE_SIZE, (page + 1) * PAGE_SIZE)

    @pytest.mark.django_db()
    def test_full_listing_with_delta(self, list_transferables: Callable, expected_ids: list[UUID]):
        response = list_transferables(page_size=PAGE_SIZE)
        current_page = response.data["pages"]["current"]
        self.assert_slice(response, expected_ids, 0, PAGE_SIZE)

        self.insert_decoy_transferables()

        for page in range(1, PAGES):
            response = list_transferables(page_size=PAGE_SIZE, from_=current_page, delta=1)
            current_page = response.data["pages"]["current"]
            self.assert_slice(response, expected_ids, page * PAGE_SIZE, (page + 1) * PAGE_SIZE)

    @pytest.mark.django_db()
    def test_page_delta(self, list_transferables: Callable, expected_ids: list[UUID]):
        response = list_transferables(page_size=PAGE_SIZE)
        current = response.data["pages"]["current"]
        self.assert_slice(response, expected_ids, 0, PAGE_SIZE)

        response = list_transferables(page_size=PAGE_SIZE, delta=1, from_=current)
        current = response.data["pages"]["current"]
        self.assert_slice(response, expected_ids, PAGE_SIZE * 1, PAGE_SIZE * 2)

        self.insert_decoy_transferables()

        response = list_transferables(page_size=PAGE_SIZE, delta=2, from_=current)
        current = response.data["pages"]["current"]
        self.assert_slice(response, expected_ids, PAGE_SIZE * 3, PAGE_SIZE * 4)

        response = list_transferables(page_size=PAGE_SIZE, delta=-2, from_=current)
        next_page = response.data["pages"]["next"]
        self.assert_slice(response, expected_ids, PAGE_SIZE * 1, PAGE_SIZE * 2)

        self.insert_decoy_transferables()

        response = list_transferables(page_size=PAGE_SIZE, delta=2, from_=next_page)
        self.assert_slice(response, expected_ids, PAGE_SIZE * 4, PAGE_SIZE * 5)

    @pytest.mark.django_db()
    def test_full_listing_with_cursor_and_page_delta_backwards(
        self, list_transferables: Callable, expected_ids: list[UUID]
    ):
        response = list_transferables(page_size=PAGE_SIZE)
        first = response.data["pages"]["current"]
        response = list_transferables(page_size=PAGE_SIZE, delta=PAGES - 1, from_=first)
        last_page = response.data["pages"]["current"]

        response = list_transferables(page_size=PAGE_SIZE, page=last_page)
        current = response.data["pages"]["current"]
        self.assert_slice(response, expected_ids, PAGE_SIZE * (PAGES - 1), PAGE_SIZE * PAGES)

        self.insert_decoy_transferables()

        for page in range(PAGES - 1, 0, -1):
            response = list_transferables(page_size=PAGE_SIZE, delta=-1, from_=current)
            current = response.data["pages"]["current"]
            self.assert_slice(response, expected_ids, (page - 1) * PAGE_SIZE, page * PAGE_SIZE)

    @pytest.mark.django_db()
    def test_full_listing_with_cursor_and_absolute_page_backwards(
        self, list_transferables: Callable, expected_ids: list[UUID]
    ):
        response = list_transferables(page_size=PAGE_SIZE)
        first = response.data["pages"]["current"]
        response = list_transferables(page_size=PAGE_SIZE, delta=PAGES - 1, from_=first)
        last_page = response.data["pages"]["current"]

        response = list_transferables(page_size=PAGE_SIZE, page=last_page)
        previous = response.data["pages"]["previous"]
        self.assert_slice(response, expected_ids, PAGE_SIZE * (PAGES - 1), PAGE_SIZE * PAGES)

        self.insert_decoy_transferables()

        for page in range(PAGES - 1, 0, -1):
            response = list_transferables(page_size=PAGE_SIZE, page=previous)
            previous = response.data["pages"]["previous"]
            self.assert_slice(response, expected_ids, (page - 1) * PAGE_SIZE, page * PAGE_SIZE)

    @pytest.mark.django_db()
    @pytest.mark.parametrize("page", [1, int(PAGES / 2), PAGES])
    def test_refresh_with_current(self, list_transferables: Callable, expected_ids: list[UUID], page: int):
        response = list_transferables(page_size=PAGE_SIZE)
        if page != 1:
            first = response.data["pages"]["current"]
            response = list_transferables(page_size=PAGE_SIZE, delta=page - 1, from_=first)
        selected_page = response.data["pages"]["current"]

        response = list_transferables(page_size=PAGE_SIZE, page=selected_page)
        current = response.data["pages"]["current"]
        self.assert_slice(response, expected_ids, (page - 1) * PAGE_SIZE, page * PAGE_SIZE)

        self.insert_decoy_transferables()

        response = list_transferables(page_size=PAGE_SIZE, page=current)
        self.assert_slice(response, expected_ids, (page - 1) * PAGE_SIZE, page * PAGE_SIZE)

    @pytest.mark.django_db()
    @pytest.mark.parametrize("page", [2, int(PAGES / 2) + 1, PAGES])
    def test_refresh_with_reverse_cursor(self, list_transferables: Callable, expected_ids: list[UUID], page: int):
        response = list_transferables(page_size=PAGE_SIZE)
        first = response.data["pages"]["current"]
        response = list_transferables(page_size=PAGE_SIZE, delta=page - 1, from_=first)
        selected_page = response.data["pages"]["previous"]

        response = list_transferables(page_size=PAGE_SIZE, page=selected_page)
        current = response.data["pages"]["current"]
        self.assert_slice(response, expected_ids, (page - 2) * PAGE_SIZE, (page - 1) * PAGE_SIZE)

        self.insert_decoy_transferables()

        response = list_transferables(page_size=PAGE_SIZE, page=current)
        self.assert_slice(response, expected_ids, (page - 2) * PAGE_SIZE, (page - 1) * PAGE_SIZE)

    @pytest.mark.django_db()
    def test_dbtrimmer_with_cursor_unchanged_pages(self, list_transferables: Callable, expected_ids: list[UUID]):
        response = list_transferables(page_size=PAGE_SIZE)
        first_page = response.data["pages"]["current"]
        response = list_transferables(page_size=PAGE_SIZE, delta=PAGES - 3, from_=first_page)
        current = response.data["pages"]["current"]
        self.assert_slice(response, expected_ids, PAGE_SIZE * (PAGES - 3), PAGE_SIZE * (PAGES - 2))

        self.trim_transferables(5 * PAGE_SIZE // 2)

        self.insert_decoy_transferables()

        response = list_transferables(page_size=PAGE_SIZE, page=current)
        self.assert_slice(
            response,
            expected_ids,
            PAGE_SIZE * (PAGES - 3),
            PAGE_SIZE * (PAGES - 3) + PAGE_SIZE // 2,
            count=PAGE_SIZE * (PAGES - 3) + PAGE_SIZE // 2,
        )

    @pytest.mark.django_db()
    def test_max_page_size(self, list_transferables: Callable, expected_ids: list[UUID]):
        backup = EurydiceSessionPagination.max_page_size
        EurydiceSessionPagination.max_page_size = 2 * PAGE_SIZE

        response = list_transferables(page_size=2 * PAGE_SIZE)
        self.assert_slice(response, expected_ids, 0, 2 * PAGE_SIZE)

        response = list_transferables(page_size=2 * PAGE_SIZE + 1)
        self.assert_slice(response, expected_ids, 0, 2 * PAGE_SIZE)

        EurydiceSessionPagination.max_page_size = backup

    @pytest.mark.django_db()
    def test_default_page_size(self, list_transferables: Callable, expected_ids: list[UUID]):
        size = api_settings.PAGE_SIZE

        response = list_transferables()
        self.assert_slice(response, expected_ids, 0, size)

    @pytest.mark.django_db()
    def test_new_items(self, list_transferables: Callable, expected_ids: list[UUID]):
        response = list_transferables(page_size=PAGE_SIZE)
        next_page = response.data["pages"]["next"]
        response = list_transferables(page_size=PAGE_SIZE, page=next_page)
        self.assert_slice(response, expected_ids, PAGE_SIZE, 2 * PAGE_SIZE)
        assert response.data["new_items"] is False
        current = response.data["pages"]["current"]
        next_page = response.data["pages"]["next"]

        response = list_transferables(page_size=PAGE_SIZE, page=current)
        self.assert_slice(response, expected_ids, PAGE_SIZE, 2 * PAGE_SIZE)
        assert response.data["new_items"] is False

        response = list_transferables(page_size=PAGE_SIZE, delta=1, from_=current)
        self.assert_slice(response, expected_ids, PAGE_SIZE * 2, PAGE_SIZE * 3)
        assert response.data["new_items"] is False

        self.insert_decoy_transferables(1)

        response = list_transferables(page_size=PAGE_SIZE, page=current)

        self.assert_slice(response, expected_ids, PAGE_SIZE, PAGE_SIZE * 2)
        assert response.data["new_items"] is True

        response = list_transferables(page_size=PAGE_SIZE, delta=1, from_=current)
        self.assert_slice(response, expected_ids, PAGE_SIZE * 2, PAGE_SIZE * 3)
        assert response.data["new_items"] is True

        response = list_transferables(page_size=PAGE_SIZE, page=next_page)
        self.assert_slice(response, expected_ids, PAGE_SIZE * 2, PAGE_SIZE * 3)
        assert response.data["new_items"] is True
