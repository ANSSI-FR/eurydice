from typing import Dict

from rest_framework import serializers

from eurydice.common import association
from eurydice.common import bytes2words


class AssociationTokenSerializer(serializers.Serializer):
    """Serialize and deserialize an AssociationToken.

    The AssociationToken is used to allow end users to associate their accounts
    between the origin and the destination API. An end user will call the origin API
    to get an AssociationToken, and copy that token over to the destination API.

    Attributes:
        token: the encoded token provided as a list of words.
        expires_at: the expiration date of the token (informational only).

    """

    token = serializers.CharField()
    expires_at = serializers.DateTimeField(read_only=True)

    def to_internal_value(self, data: dict) -> association.AssociationToken:
        """Deserialize data to validated AssociationToken."""
        words = super().to_internal_value(data)["token"]

        try:
            return association.AssociationToken.from_bytes(bytes2words.decode(words))
        except (bytes2words.DecodingError, association.MalformedToken):
            raise serializers.ValidationError({"token": "Malformed token."})
        except association.InvalidTokenDigest:
            raise serializers.ValidationError(
                {"token": "Invalid association token signature."}
            )
        except association.ExpiredToken:
            raise serializers.ValidationError(
                {"token": "The association token has expired."}
            )

    def to_representation(
        self, instance: association.AssociationToken
    ) -> Dict[str, str]:
        """Serialize the AssociationToken to a dictionary representation."""
        instance.verify_validity_time()

        return {
            "token": bytes2words.encode(instance.to_bytes()),
            "expires_at": self.fields["expires_at"].to_representation(
                instance.expires_at
            ),
        }


__all__ = ("AssociationTokenSerializer",)
