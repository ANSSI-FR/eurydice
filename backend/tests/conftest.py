import factory.random
import pytest
from django.conf import settings
from rest_framework import test


@pytest.fixture(autouse=True, scope="session")
def _whitenoise_autorefresh() -> None:
    """Get rid of whitenoise "No directory at" warning,
    as it's not helpful when running tests.

    Related:
        - https://github.com/evansd/whitenoise/issues/215
        - https://github.com/evansd/whitenoise/issues/191
        - https://github.com/evansd/whitenoise/commit/4204494d44213f7a51229de8bc224cf6d84c01eb  # noqa: E501
    """
    settings.WHITENOISE_AUTOREFRESH = True


@pytest.fixture(autouse=True, scope="session")
def _setup_factory_boy() -> None:
    """Set the default random seed value used by factory_boy."""
    factory.random.reseed_random(settings.FAKER_SEED)


@pytest.fixture(autouse=True, scope="session")
def faker_seed() -> int:
    """Set the default random seed value used by Faker."""
    return settings.FAKER_SEED


@pytest.fixture()
def api_client() -> test.APIClient:
    return test.APIClient()
