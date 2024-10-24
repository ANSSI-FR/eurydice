"""Custom permissions for the destination API."""

from django.utils.translation import gettext_lazy as _
from rest_framework import permissions
from rest_framework import request as drf_request
from rest_framework import views

from eurydice.destination.core import models


def _is_associated_user(user: models.User) -> bool:
    """
    Args:
        user (models.User): the user to check for association

    Returns:
        Whether this user is associated
    """
    return (
        models.User.objects.filter(
            id=user.id,
            user_profile__associated_user_profile_id__isnull=False,
        )
        .only("id")
        .exists()
    )


class IsAssociatedUser(permissions.IsAuthenticated):  # type: ignore
    """
    Permission to only allow actions to a user that has undergone association.
    """

    message = _(
        "Your destination user account must be associated with its origin user account."
    )

    def has_permission(
        self,
        request: drf_request.Request,
        view: views.APIView,
    ) -> bool:
        """
        Check whether request's user is authenticated and associated

        Args:
            request (drf_request.Request): the request from the user
            view (views.APIView): the view associated with the request

        Returns:
            whether user is authenticated and associated
        """

        is_authenticated = super().has_permission(request, view)
        is_associated = False

        if is_authenticated:
            # NOTE: user is authenticated, so request.user is not None
            is_associated = _is_associated_user(request.user)  # type: ignore

        return is_authenticated and is_associated
