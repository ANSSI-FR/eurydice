from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


class UserSerializer(serializers.Serializer):
    """Serialize a User.

    Attributes:
        username: the username of the User.

    """

    username = serializers.CharField(
        help_text=_("The username of the User"),
    )
