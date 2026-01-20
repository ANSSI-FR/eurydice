from pathlib import Path
from unittest import mock

import faker
import freezegun
from django.db import models
from django.utils import timezone

from eurydice.origin.api.views.outgoing_transferable import get_transferable_file_path
from eurydice.origin.core.models import outgoing_transferable


def test_PythonNow(faker: faker.Faker):  # noqa: N802
    now = outgoing_transferable.PythonNow()
    assert now.value is None

    fake_datetime = faker.date_time_this_decade(tzinfo=timezone.get_current_timezone())
    with (
        freezegun.freeze_time(fake_datetime),
        mock.patch.object(
            models.Value,
            "as_sql",
            return_value="",
        ) as patched_now_as_sql,
    ):
        now.as_sql()
        patched_now_as_sql.assert_called_once()
        assert now.value == fake_datetime


def test_get_target_file_path():
    assert get_transferable_file_path("123456789") == Path("/tmp/eurydice-test/data/123456789")
