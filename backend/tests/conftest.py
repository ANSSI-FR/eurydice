from pathlib import Path

import factory.random
import pytest
from django.conf import settings
from rest_framework import test

from tests.common.decryption_constants import PRIVKEY, PUBKEY


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


@pytest.fixture(autouse=True, scope="session")
def _create_encryption_keys() -> None:
    settings.PUBKEY_PATH = "/tmp/eurydice-test/keys/eurydice.pub"

    pubkey_path = Path(settings.PUBKEY_PATH)
    pubkey_path.parent.mkdir(exist_ok=True, parents=True)
    pubkey_path.write_bytes(PUBKEY)

    if hasattr(settings, "ROOT_URLCONF") and "destination" in settings.ROOT_URLCONF:
        settings.PRIVKEY_PATH = "/tmp/eurydice-test/keys/eurydice"

        privkey_path = Path(settings.PRIVKEY_PATH)
        privkey_path.parent.mkdir(exist_ok=True, parents=True)
        privkey_path.write_bytes(PRIVKEY)


@pytest.fixture(autouse=True, scope="session")
def _create_transferables_test_folder() -> None:
    folder_path = Path(settings.TRANSFERABLE_STORAGE_DIR)
    folder_path.mkdir(exist_ok=True, parents=True)


@pytest.fixture()
def api_client() -> test.APIClient:
    return test.APIClient()
