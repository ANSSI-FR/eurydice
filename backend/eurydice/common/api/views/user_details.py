import logging
from typing import cast

from rest_framework import generics
from rest_framework import permissions

from eurydice.common import models
from eurydice.common.api import serializers
from eurydice.common.api.docs import decorators as documentation

logger = logging.getLogger(__name__)


@documentation.user_details
class UserDetailsView(generics.RetrieveAPIView):
    """Access details about the current authenticated user."""

    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self) -> models.AbstractUser:
        """Returns current User."""
        return cast(models.AbstractUser, self.request.user)  # the user is authenticated


__all__ = ("UserDetailsView",)
