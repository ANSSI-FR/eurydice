import collections

import pytest
from django import conf
from django.utils import timezone
from faker import Faker
from rest_framework import serializers as drf_serializers

from eurydice.common import association
from eurydice.common import bytes2words
from eurydice.common.api import serializers


class TestAssociationTokenSerializer:
    def test_to_internal_value_success(self, faker: Faker):
        obj = association.AssociationToken(user_profile_id=faker.uuid4(cast_to=None))
        deserialized_obj = serializers.AssociationTokenSerializer().to_internal_value(
            {"token": bytes2words.encode(obj.to_bytes())}
        )

        assert isinstance(deserialized_obj, association.AssociationToken)
        assert obj.user_profile_id == deserialized_obj.user_profile_id
        assert obj.expires_at == deserialized_obj.expires_at
        assert obj.digest == deserialized_obj.digest

    @pytest.mark.parametrize(
        "value",
        [
            bytes2words.encode(
                b"\xddy\xba\xe1\x85\x8c\x0c6\xdai\xacw\x0clq"
                b"\xe4\xb0\xf4\xc1\x0cs\xacf\t\rO\x07\xa0e3P\x80\xd4\xee"
            ),
            "abusif potatoe",
        ],
    )
    def test_to_internal_value_error_malformed_token(self, value: str):
        with pytest.raises(
            drf_serializers.ValidationError,
            match="Malformed token.",
        ):
            serializers.AssociationTokenSerializer().to_internal_value({"token": value})

    def test_to_internal_value_error_invalid_token_signature(
        self, settings: conf.Settings, faker: Faker
    ):
        settings.USER_ASSOCIATION_TOKEN_SECRET_KEY = (
            "kzuzabvqkcc8b4frle16pptynbrlyo6pmfvx"
        )
        forged_token_bytes = association.AssociationToken(
            user_profile_id=faker.uuid4(cast_to=None)
        ).to_bytes()

        settings.USER_ASSOCIATION_TOKEN_SECRET_KEY = (
            "14amnpyopw7f2xd8tok5tl8rr9jsnbti2vgx"
        )

        with pytest.raises(
            drf_serializers.ValidationError,
            match="Invalid association token signature.",
        ):
            serializers.AssociationTokenSerializer().to_internal_value(
                {"token": bytes2words.encode(forged_token_bytes)}
            )

    def test_to_internal_value_error_expired_token(self, faker: Faker):
        token = association.AssociationToken(
            user_profile_id=faker.uuid4(cast_to=None),
            expires_at=faker.date_time_this_decade(
                tzinfo=timezone.get_current_timezone()
            ),
        )

        with pytest.raises(
            drf_serializers.ValidationError, match="The association token has expired."
        ):
            serializers.AssociationTokenSerializer().to_internal_value(
                {"token": bytes2words.encode(token.to_bytes())}
            )

    def test_to_representation_success(self, faker: Faker):
        token = association.AssociationToken(user_profile_id=faker.uuid4(cast_to=None))
        serialized = serializers.AssociationTokenSerializer().to_representation(token)

        assert isinstance(serialized, collections.abc.Mapping)
        assert isinstance(serialized["token"], str)
        assert isinstance(serialized["expires_at"], str)

    def test_to_representation_error_expired_token(self, faker: Faker):
        token = association.AssociationToken(
            user_profile_id=faker.uuid4(cast_to=None),
            expires_at=faker.date_time_this_decade(
                tzinfo=timezone.get_current_timezone()
            ),
        )

        with pytest.raises(association.ExpiredToken):
            serializers.AssociationTokenSerializer().to_representation(token)


@pytest.mark.parametrize(
    ("representation", "value"),
    [
        (
            "6c6120766172696174696f6e206475205049422064616e73206c65206d6f6e64652073"
            "7569742074726573206578616374656d656e74206c6120766172696174696f6e206465"
            "206c61207175616e7469746520646520706574726f6c652070726f6475697465",
            b"la variation du PIB dans le monde suit tres exactement "
            b"la variation de la quantite de petrole produite",
        ),
    ],
)
class TestBytesAsHexadecimalField:
    def test_to_internal_value_success(self, representation: str, value: bytes):
        assert (
            serializers.BytesAsHexadecimalField().to_internal_value(representation)
            == value
        )

    def test_to_representation_success(self, representation: str, value: bytes):
        assert (
            serializers.BytesAsHexadecimalField().to_representation(value)
            == representation
        )
