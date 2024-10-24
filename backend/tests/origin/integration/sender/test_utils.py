from typing import Optional

import django.core.exceptions as django_exceptions
import pytest
from django.conf import Settings

import eurydice.origin.sender.utils as sender_utils


@pytest.mark.parametrize(
    ("lidis_host", "lidis_port", "expected_exception"),
    [
        (None, None, django_exceptions.ImproperlyConfigured),
        ("127.0.0.1", None, django_exceptions.ImproperlyConfigured),
        (None, 666, django_exceptions.ImproperlyConfigured),
        ("127.0.0.1", 666, None),
    ],
)
def test_loop_exception_missing_lidis_address(
    lidis_host: Optional[str],
    lidis_port: Optional[int],
    expected_exception: Optional[django_exceptions.ImproperlyConfigured],
    settings: Settings,
):
    settings.LIDIS_HOST = lidis_host
    settings.LIDIS_PORT = lidis_port

    if expected_exception is None:
        sender_utils.check_configuration()
    else:
        with pytest.raises(expected_exception):
            sender_utils.check_configuration()
