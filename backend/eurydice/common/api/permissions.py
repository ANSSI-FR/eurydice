"""A set of permission policies."""

from django import http
from django.utils.translation import gettext as _
from rest_framework import permissions, views
from rest_framework import request as drf_request

from eurydice.common import models


class IsTransferableOwner(permissions.IsAuthenticated):  # type: ignore
    """
    Object-level permission to only allow the owner of a Transferable
    (OutgoingTransferable or IncomingTransferable) to access it.

    Assumes that the object has a relation with a User through a
    UserProfile.
    """

    def has_object_permission(  # noqa: D102
        self,
        request: drf_request.Request,
        view: views.APIView,
        obj: models.AbstractBaseModel,
    ) -> bool:
        if (
            type(obj)  # type: ignore[misc]
            # Using _default_manager, see:
            # https://docs.djangoproject.com/fr/2.2/topics/db/managers/#django.db.models.Model._default_manager
            ._default_manager.filter(
                id=obj.id,
                user_profile__user__id=request.user.id,  # type: ignore[union-attr]
            )
            .exists()
        ):
            return True

        raise http.Http404


class CanViewMetrics(permissions.IsAuthenticated):  # type: ignore
    """
    Permission to only allow administrators and explicitly authorized
    users to view rolling metrics.
    """

    message = _("You do not have permission to view metrics, please contact an administrator if you think you should.")

    def has_permission(self, request: drf_request.Request, view: views.APIView) -> bool:
        """Returns true if and only if the current user is allowed to view metrics."""
        return super().has_permission(request, view) and request.user.has_perm(  # type: ignore[union-attr]
            "eurydice_common_permissions.view_rolling_metrics"
        )
