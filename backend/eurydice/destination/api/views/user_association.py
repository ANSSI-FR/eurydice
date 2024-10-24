from typing import cast

from django.contrib import auth
from rest_framework import request as drf_request
from rest_framework import response as drf_response
from rest_framework import status
from rest_framework import views

from eurydice.common import association
from eurydice.common.api import serializers
from eurydice.destination.api import exceptions
from eurydice.destination.api.docs import decorators as documentation
from eurydice.destination.core import models


def _user_is_associated(user: models.User) -> bool:
    return (
        auth.get_user_model()
        .objects.filter(id=user.id, user_profile__isnull=False)
        .exists()
    )


def _user_profile_in_token_associated(token: association.AssociationToken) -> bool:
    return models.UserProfile.objects.filter(
        associated_user_profile_id=token.user_profile_id, user__isnull=False
    ).exists()


def _perform_association(
    user: models.User, token: association.AssociationToken
) -> None:
    models.UserProfile.objects.update_or_create(
        associated_user_profile_id=token.user_profile_id,
        defaults={"user": user},
    )


@documentation.user_association
class UserAssociationView(views.APIView):  # noqa: D101
    def post(
        self, request: drf_request.Request, *args, **kwargs
    ) -> drf_response.Response:
        """Submit an association token obtained from the origin API to associate a user
        on the origin side with a user on this side.

        Raises:
            AlreadyAssociatedError: when the current authenticated user is already
                associated with a user from the origin side.

        Returns:
            A DRF Response of status 204 when the association succeeded.

        """
        serializer = serializers.AssociationTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = cast(models.User, request.user)  # the user is authenticated

        token = serializer.validated_data

        if _user_is_associated(user) or _user_profile_in_token_associated(token):
            raise exceptions.AlreadyAssociatedError

        _perform_association(user=user, token=token)
        return drf_response.Response(status=status.HTTP_204_NO_CONTENT)


__all__ = ("UserAssociationView",)
