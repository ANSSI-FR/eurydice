import collections.abc
from typing import Any

from django.conf import settings
from django.core import exceptions, validators
from django.db import models


class TransferableNameField(models.CharField):
    """A field to store the name of a Transferable."""

    MIN_LENGTH: int = 1
    MAX_LENGTH: int = 255

    def __init__(self, *args, **kwargs) -> None:
        kwargs["validators"] = (validators.MinLengthValidator(TransferableNameField.MIN_LENGTH),)
        kwargs["max_length"] = TransferableNameField.MAX_LENGTH
        super().__init__(*args, **kwargs)


class TransferableSizeField(models.PositiveBigIntegerField):
    """A field to store the size in bytes of a Transferable."""

    def __init__(self, *args, **kwargs) -> None:
        kwargs["validators"] = (validators.MaxValueValidator(settings.TRANSFERABLE_MAX_SIZE),)
        super().__init__(*args, **kwargs)


class SHA1Field(models.BinaryField):
    """A field to store the SHA-1 of a file in a binary format."""

    DIGEST_SIZE_IN_BYTES: int = 20

    def __init__(self, *args, **kwargs) -> None:
        kwargs["validators"] = (validators.MinLengthValidator(SHA1Field.DIGEST_SIZE_IN_BYTES),)
        kwargs["max_length"] = SHA1Field.DIGEST_SIZE_IN_BYTES
        super().__init__(*args, **kwargs)


class UserProvidedMetaField(models.JSONField):
    """A field to store Transferable metadata provided by the user as JSON."""

    def validate(self, field_value: Any, model_instance: models.Model | None) -> None:
        """
        Validate that the field contains a mapping of str to str with keys
        starting with settings.METADATA_HEADER_PREFIX, and that the keys are
        case insensitive.
        """

        super().validate(field_value, model_instance)  # type: ignore[arg-type]
        self._validate_is_mapping(field_value)

        for key, value in field_value.items():
            self._validate_mapping_key(key)
            self._validate_mapping_value(value)

        self._validate_unique_lowercase_mapping_keys(field_value)

    def _validate_is_mapping(self, field_value: Any) -> None:
        if not isinstance(field_value, collections.abc.Mapping):
            raise exceptions.ValidationError("Value must be a mapping.")

    def _validate_mapping_key(self, key: Any) -> None:
        if not isinstance(key, str):
            raise exceptions.ValidationError("Keys of the mapping must be strings.")

        if not key.startswith(settings.METADATA_HEADER_PREFIX):
            raise exceptions.ValidationError(f"Metadata item names must start with {settings.METADATA_HEADER_PREFIX}")

    def _validate_mapping_value(self, value: Any) -> None:
        if not isinstance(value, str):
            raise exceptions.ValidationError("Metadata item contents must be strings.")

    def _validate_unique_lowercase_mapping_keys(self, field_value: dict[str, str]) -> None:
        lowercase_keys = [k.lower() for k in field_value.keys()]
        if len(set(lowercase_keys)) != len(lowercase_keys):
            raise exceptions.ValidationError("Metadata item names are case insensitive and must not be duplicated.")


__all__ = (
    "TransferableNameField",
    "TransferableSizeField",
    "SHA1Field",
    "UserProvidedMetaField",
)
