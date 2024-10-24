import datetime
import hmac
import struct
import uuid
from typing import Optional

from django.conf import settings
from django.utils import crypto
from django.utils import timezone


class MalformedToken(ValueError):
    """The provided token bytes don't match the expected shape."""


class InvalidTokenDigest(ValueError):
    """The signature of the token does not match its body."""


class ExpiredToken(ValueError):
    """The validity period of the token is over."""


class AssociationToken:
    """A token representing a UserProfile by its UUID (user_profile_id), that expires at
    a given datetime (expires_at), and signed with a hmac_md5 (digest).

    To generate a new AssociationToken, users should call the constructor providing
    only one argument, the user_profile_id. This will let the instance set its
    own expiration time. That token can then be serialized into bytes, with the
    to_bytes method.

    Example:
        token = AssociationToken(user_profile_id)
        token_bytes = token.to_bytes()
        ...
        token = AssociationToken.from_bytes(token_bytes)
        user_profile_id = token.user_profile_id

    Attributes:
        user_profile_id: uuid of a UserProfile
        expires_at: (optional) after this datetime the token will no longer be valid.
            If unspecified, is set automatically.
        digest: md5 of the user_profile_id + expires_at (as 4 bytes)

    """

    _BYTE_ORDER = ">"
    _UUID_FORMAT = "16s"
    _TIMESTAMP_FORMAT = "I"
    _HMAC_FORMAT = "16s"
    _BODY_FORMAT = _BYTE_ORDER + _UUID_FORMAT + _TIMESTAMP_FORMAT
    _TOKEN_FORMAT = _BODY_FORMAT + _HMAC_FORMAT

    def __init__(
        self,
        user_profile_id: uuid.UUID,
        expires_at: Optional[datetime.datetime] = None,
    ):
        self.user_profile_id: uuid.UUID = user_profile_id
        self.expires_at: datetime.datetime = expires_at  # type: ignore

    @property
    def expires_at(self) -> datetime.datetime:
        """Returns the token expiration datetime."""
        return self._expires_at

    @expires_at.setter
    def expires_at(self, value: Optional[datetime.datetime]) -> None:
        """Sets the token expiration datetime."""
        if value is None:
            value = timezone.now() + datetime.timedelta(
                seconds=settings.USER_ASSOCIATION_TOKEN_EXPIRES_AFTER
            )
        elif timezone.is_naive(value):
            raise ValueError(
                "Received naive datetime instead of timezone aware datetime"
            )

        # remove microseconds as they are lost when serializing the token to bytes
        self._expires_at = value.replace(microsecond=0)

    @property
    def digest(self) -> bytes:
        """Returns a computed HMAC digest from this AssociationToken.

        Returns:
            bytes representing the computed hmac_md5.

        """

        body = struct.pack(
            self._BODY_FORMAT,
            self.user_profile_id.bytes,
            int(self.expires_at.timestamp()),
        )

        return hmac.digest(
            settings.USER_ASSOCIATION_TOKEN_SECRET_KEY.encode("utf-8"),
            body,
            "md5",
        )

    def verify_digest(self, digest: bytes) -> None:
        """Checks the provided digest against a digest computed from the present token.

        Raises:
            InvalidTokenDigest: if the digests don't match.

        """

        if not crypto.constant_time_compare(digest, self.digest):
            raise InvalidTokenDigest()

    def verify_validity_time(self) -> None:
        """Checks that the validity period of the token is not over.

        Raises:
            ExpiredToken: if the token has expired.

        """

        if timezone.now() > self.expires_at:
            raise ExpiredToken()

    def verify(self, digest: bytes) -> None:
        """Checks the integrity of this AssociationToken.

        Raises:
            InvalidTokenDigest: if the provided digest don't match the body of
                the token.
            ExpiredToken: if the token has expired.

        """

        self.verify_digest(digest)
        self.verify_validity_time()

    def to_bytes(self) -> bytes:
        """Serializes an AssociationToken to bytes.

        Returns: bytes consisting of the user_profile_id, the expiration timestamp, and
            the hmac_md5 packed together.

        """

        return struct.pack(
            self._TOKEN_FORMAT,
            self.user_profile_id.bytes,
            int(self.expires_at.timestamp()),
            self.digest,
        )

    @classmethod
    def from_bytes(cls, value: bytes) -> "AssociationToken":
        """Deserializes an AssociationToken from bytes and verifies it.

        Args:
            value: bytes to deserialize.

        Returns:
            AssociationToken

        Raises:
            MalformedToken: if the token cannot be deserialized.
            InvalidTokenDigest: if the signature digest doesn't match the body of
                the token.
            ExpiredToken: if the token has expired.

        """

        try:
            uuid_bytes, timestamp, hmac_md5 = struct.unpack(cls._TOKEN_FORMAT, value)
        except struct.error:
            raise MalformedToken()

        user_profile_id = uuid.UUID(bytes=uuid_bytes)
        expires_at = datetime.datetime.fromtimestamp(
            timestamp, tz=timezone.get_current_timezone()
        )

        obj = cls(user_profile_id, expires_at)
        obj.verify(hmac_md5)
        return obj


__all__ = ("AssociationToken",)
