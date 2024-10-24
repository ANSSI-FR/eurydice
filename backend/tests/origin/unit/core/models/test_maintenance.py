import pytest
from django.db.utils import IntegrityError

from eurydice.origin.core.models.maintenance import Maintenance


@pytest.mark.django_db()
def test_cant_create_other_maintenance_instance() -> None:
    with pytest.raises(IntegrityError):
        Maintenance.objects.create(maintenance=True)
