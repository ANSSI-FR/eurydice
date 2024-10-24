import pytest
from django.contrib import auth
from django.core.management import call_command

from eurydice.origin.core import models


@pytest.mark.django_db()
def test_populate_db():
    args = []
    opts = {"users": 1, "outgoing_transferables": 2, "transferable_ranges": 3}
    call_command("populate_db", *args, **opts)

    assert models.UserProfile.objects.count() == opts["users"]
    assert auth.get_user_model().objects.count() == opts["users"]
    assert models.OutgoingTransferable.objects.count() == opts["outgoing_transferables"]
    assert models.TransferableRange.objects.count() == opts["transferable_ranges"]
