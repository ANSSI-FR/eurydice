import pytest
from rest_framework import test

from tests.common.integration.endpoints import metadata


@pytest.mark.django_db()
def test_metadata(api_client: test.APIClient):
    metadata.metadata(api_client)
