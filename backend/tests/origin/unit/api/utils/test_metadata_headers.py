from typing import Dict

import pytest

from eurydice.origin.api.utils import metadata_headers


@pytest.mark.parametrize(
    ("headers", "expected"),
    [
        # Test expected header
        ({"Metadata-Name": "OSS117"}, {"Metadata-Name": "OSS117"}),
        # Test one incorrect header
        ({"X-Metadata-Name": "OSS117"}, {}),
        # Test one incorrect header with a correct one
        (
            {
                "Choose-Life": "Choose a job. Choose a career...",
                "Metadata-agent": "007",
            },
            {"Metadata-agent": "007"},
        ),
    ],
)
def test_extract_metadata_from_headers(
    headers: Dict[str, str], expected: Dict[str, str]
):
    assert (
        metadata_headers.extract_metadata_from_headers(headers)  # type: ignore
        == expected
    )
