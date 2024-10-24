import django.core.exceptions as django_exceptions
from django.conf import settings


def check_configuration() -> None:
    """Verify LIDIS configuration

    Raises:
        django_exceptions.ImproperlyConfigured: when LIDIS_HOST or PORT is missing
    """
    if not all((settings.LIDIS_HOST, settings.LIDIS_PORT)):
        raise django_exceptions.ImproperlyConfigured(
            "Both LIDIS_HOST and LIDIS_PORT environment variables must be defined"
        )


__all__ = ("check_configuration",)
