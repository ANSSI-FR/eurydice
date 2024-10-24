import datetime
from typing import Optional

import pytest
from django.conf import settings
from django.utils import timezone

from eurydice.destination.cleaning.s3remover.s3remover import DestinationS3Remover


@pytest.mark.parametrize(
    ("last_clean_at", "expected"),
    [
        (None, True),
        (timezone.now() - settings.S3REMOVER_RUN_EVERY, True),
        (timezone.now() + datetime.timedelta(minutes=60), False),
    ],
)
def test_should_clean_success(
    last_clean_at: Optional[datetime.datetime], expected: bool
):
    s3remover = DestinationS3Remover()
    s3remover._last_run_at = last_clean_at
    assert s3remover._should_run() is expected
