import datetime
from typing import Optional

import pytest
from django.conf import settings
from django.utils import timezone

from eurydice.destination.cleaning.file_remover.file_remover import (
    DestinationFileRemover,
)


@pytest.mark.parametrize(
    ("last_clean_at", "expected"),
    [
        (None, True),
        (timezone.now() - settings.FILE_REMOVER_RUN_EVERY, True),
        (timezone.now() + datetime.timedelta(minutes=60), False),
    ],
)
def test_should_clean_success(
    last_clean_at: Optional[datetime.datetime], expected: bool
):
    file_remover = DestinationFileRemover()
    file_remover._last_run_at = last_clean_at
    assert file_remover._should_run() is expected
