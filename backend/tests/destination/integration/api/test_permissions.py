from unittest import mock

import pytest
from django import http
from faker import Faker

from eurydice.common.api import permissions
from tests.destination.integration import factory


@pytest.mark.django_db()
class TestIsTransferableOwner:
    def test_has_object_permission_authorized(self):
        obj = factory.IncomingTransferableFactory()
        request = mock.Mock()
        request.user.id = obj.user_profile.user.id

        assert permissions.IsTransferableOwner.has_object_permission(
            self=None, request=request, view=None, obj=obj
        )

    def test_has_object_permission_unauthorized(self, faker: Faker):
        obj = factory.IncomingTransferableFactory()
        request = mock.Mock()
        request.user.id = faker.uuid4(cast_to=None)

        with pytest.raises(http.Http404):
            permissions.IsTransferableOwner.has_object_permission(
                self=None, request=request, view=None, obj=obj
            )
