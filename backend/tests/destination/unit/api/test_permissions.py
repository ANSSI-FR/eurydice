from unittest import mock

import pytest
from rest_framework import request
from rest_framework import views

from eurydice.destination.api import permissions
from tests.destination.integration import factory


@pytest.mark.django_db()
def test__is_associated_user_when_user_is_associated():
    user = factory.UserFactory()
    factory.UserProfileFactory(user=user)
    assert permissions._is_associated_user(user) is True


@pytest.mark.django_db()
def test__is_associated_user_when_user_is_not_associated():
    user = factory.UserFactory()
    assert permissions._is_associated_user(user) is False


@pytest.mark.parametrize(
    ("is_authenticated", "is_associated", "expected_result"),
    [
        (False, False, False),
        (True, False, False),
        (False, True, False),
        (True, True, True),
    ],
)
@mock.patch(
    "eurydice.destination.api.permissions.permissions.IsAuthenticated.has_permission"
)
@mock.patch("eurydice.destination.api.permissions._is_associated_user")
def test_is_associated_user_has_permission(
    mocked_is_authenticated_has_permission: mock.Mock,
    mocked__is_associated_user: mock.Mock,
    is_authenticated: bool,
    is_associated: bool,
    expected_result: bool,
):
    mocked_is_authenticated_has_permission.return_value = is_authenticated

    mocked__is_associated_user.return_value = is_associated

    mocked_is_associated_user = mock.Mock(spec=permissions.IsAssociatedUser)

    mocked_request = mock.Mock(spec=request.Request)
    mocked_view = mock.Mock(spec=views.APIView)

    assert (
        permissions.IsAssociatedUser.has_permission(
            mocked_is_associated_user, mocked_request, mocked_view
        )
        is expected_result
    )
