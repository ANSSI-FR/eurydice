from typing import Dict

import pytest
from django.conf import settings
from django.core import exceptions

import eurydice.common.models.fields as fields


class TestUserProvidedMetaField:
    @pytest.mark.parametrize(
        ("field_value", "error_message"),
        [
            ([], "Value must be a mapping."),
            ({1: "foo"}, "Keys of the mapping must be strings."),
            (
                {"": "foo"},
                f"Metadata item names must start with "
                f"{settings.METADATA_HEADER_PREFIX}.",
            ),
            (
                {"Bar": "foo"},
                f"Metadata item names must start with "
                f"{settings.METADATA_HEADER_PREFIX}.",
            ),
            (
                {f"{settings.METADATA_HEADER_PREFIX}Bar": 42},
                "Metadata item contents must be strings.",
            ),
            (
                {
                    f"{settings.METADATA_HEADER_PREFIX}Bar": "hello",
                    f"{settings.METADATA_HEADER_PREFIX}bar": "world",
                },
                "Metadata item names are case insensitive and must not be duplicated.",
            ),
        ],
    )
    def test_validate_error(self, field_value: Dict[str, str], error_message: str):
        with pytest.raises(exceptions.ValidationError) as exc_info:  # noqa: PT012
            fields.UserProvidedMetaField(blank=True).validate(field_value, None)

            assert exc_info.value.message == error_message

    @pytest.mark.parametrize(
        "field_value",
        [
            {},
            {f"{settings.METADATA_HEADER_PREFIX}Bar": "Baz"},
            {
                f"{settings.METADATA_HEADER_PREFIX}Bar": "Baz",
                f"{settings.METADATA_HEADER_PREFIX}Baz": "Xyz",
            },
        ],
    )
    def test_validate_success(self, field_value: Dict[str, str]):
        fields.UserProvidedMetaField(blank=True).validate(field_value, None)
