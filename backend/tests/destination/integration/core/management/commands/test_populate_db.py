import pytest
from django.contrib import auth
from django.core.management import call_command

from eurydice.destination.core import models


@pytest.mark.django_db()
def test_populate_db():
    args = []
    opts = {"users": 1, "incoming_transferables": 2, "file_uploaded_parts": 3}
    call_command("populate_db", *args, **opts)

    assert models.UserProfile.objects.count() == opts["users"]
    assert auth.get_user_model().objects.count() == opts["users"]
    assert models.IncomingTransferable.objects.count() == opts["incoming_transferables"]
    assert models.FileUploadPart.objects.count() == opts["file_uploaded_parts"]
