import pytest
from rest_framework import test

from tests.common.integration.endpoints import metadata


@pytest.mark.django_db()
def test_metadata(api_client: test.APIClient):
    response = metadata.metadata(api_client)

    assert (
        response.data["encoded_public_key"] == "gtC32LH1n6qCbkqQog/QwAr7TjxuED2+85o1CRlSl2Y="
        or response.data["encoded_public_key"] == ""
    )

    assert len(response.data) == 5
