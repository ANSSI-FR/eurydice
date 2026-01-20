import datetime

import freezegun
import pytest
from django.conf import Settings
from django.utils import timezone
from faker import Faker

from eurydice.common import association


class TestAssociationToken:
    @pytest.fixture()
    def token(self, faker: Faker) -> association.AssociationToken:
        return association.AssociationToken(user_profile_id=faker.uuid4(cast_to=None))

    def test_encode_decode_success(self, token: association.AssociationToken):
        token_bytes = token.to_bytes()
        token_from_bytes = association.AssociationToken.from_bytes(token_bytes)

        assert token_from_bytes.user_profile_id == token.user_profile_id
        assert token_from_bytes.expires_at == token.expires_at
        assert token_from_bytes.digest == token.digest

    @pytest.mark.parametrize("byte_length", [0, 35, 37])
    def test_decode_error_malformed(self, byte_length: int, faker: Faker):
        with pytest.raises(association.MalformedToken):
            association.AssociationToken.from_bytes(faker.binary(byte_length))

    def test_decode_error_forged_signature(self, settings: Settings, faker: Faker):
        settings.USER_ASSOCIATION_TOKEN_SECRET_KEY = "kzuzabvqkcc8b4frle16pptynbrlyo6pmfvx"
        forged_token_bytes = association.AssociationToken(user_profile_id=faker.uuid4(cast_to=None)).to_bytes()

        settings.USER_ASSOCIATION_TOKEN_SECRET_KEY = "14amnpyopw7f2xd8tok5tl8rr9jsnbti2vgx"
        with pytest.raises(association.InvalidTokenDigest):
            association.AssociationToken.from_bytes(forged_token_bytes)

    def test_decode_error_expired_token(self, token: association.AssociationToken, faker: Faker) -> None:
        token.expires_at = faker.date_time_this_decade(tzinfo=timezone.get_current_timezone())
        token_bytes = token.to_bytes()

        with pytest.raises(association.ExpiredToken):
            association.AssociationToken.from_bytes(token_bytes)

    @freezegun.freeze_time("2021-05-19 03:21:34.123456")
    def test_set_expires_at_None_success(  # noqa: N802
        self, settings: Settings, token: association.AssociationToken
    ) -> None:
        token._expires_at = None

        assert token.expires_at is None

        token.expires_at = None
        assert token.expires_at == timezone.now().replace(microsecond=0) + datetime.timedelta(
            seconds=settings.USER_ASSOCIATION_TOKEN_EXPIRES_AFTER
        )

    @freezegun.freeze_time("2021-05-19 03:21:34.123456")
    def test_set_expires_at_tz_aware_datetime_success(self, token: association.AssociationToken) -> None:
        token._expires_at = None

        assert token.expires_at is None

        token.expires_at = timezone.now()
        assert token.expires_at == timezone.now().replace(microsecond=0)
