from rest_framework import request as drf_request
from rest_framework import response as drf_response
from rest_framework import views

from eurydice.common import association
from eurydice.common.api import serializers
from eurydice.origin.api.docs import decorators as documentation


@documentation.user_association
class UserAssociationView(views.APIView):  # noqa: D101
    def get(
        self, request: drf_request.Request, *args, **kwargs
    ) -> drf_response.Response:
        """Generate an association token for a user."""
        user_profile_id = request.user.user_profile.id  # type: ignore
        token = association.AssociationToken(user_profile_id)

        serializer = serializers.AssociationTokenSerializer(token)
        return drf_response.Response(serializer.data)
