from unittest import mock

import pytest

from eurydice.origin.core import models
from tests.origin.integration import factory


@pytest.mark.django_db()
def test_user_save_signal_create_userprofile():
    """
    Assert a UserProfile is created when a User is created
    """

    # Assert signal is called on model instance save
    user = factory.UserFactoryWithSignal()
    assert models.UserProfile.objects.filter(user__id=user.id).exists()

    # Assert signal is not called when model is updated
    user.first_name = "Hubert"
    user.last_name = "Bonisseur de La Bath"

    with mock.patch.object(models.UserProfile.objects, "create", return_value=None) as mock_create:
        user.save()

        assert not mock_create.called
