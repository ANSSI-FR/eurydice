import os
import subprocess
import sys

import pytest
from django.conf import settings

from eurydice.origin.cleaning import dbtrimmer


@pytest.mark.django_db()
def test_start_and_graceful_shutdown():
    with subprocess.Popen(
        [sys.executable, "-m", dbtrimmer.__name__],
        cwd=os.path.dirname(settings.BASE_DIR),
        stderr=subprocess.PIPE,
        env={
            "DB_NAME": settings.DATABASES["default"]["NAME"],
            "DB_USER": settings.DATABASES["default"]["USER"],
            "DB_PASSWORD": settings.DATABASES["default"]["PASSWORD"],
            "DB_HOST": settings.DATABASES["default"]["HOST"],
            "DB_PORT": str(settings.DATABASES["default"]["PORT"]),
            "TRANSFERABLE_STORAGE_DIR": settings.TRANSFERABLE_STORAGE_DIR,
            "LIDIS_HOST": settings.LIDIS_HOST,
            "LIDIS_PORT": str(settings.LIDIS_PORT),
            "USER_ASSOCIATION_TOKEN_SECRET_KEY": settings.USER_ASSOCIATION_TOKEN_SECRET_KEY,  # noqa: E501
        },
    ) as proc:
        while b"Ready" not in proc.stderr.readline():
            pass

        proc.terminate()
        return_code = proc.wait()
        assert return_code == 0
