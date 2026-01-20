from django.contrib.auth.models import AnonymousUser
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.request import Request
from rest_framework.response import Response

from eurydice.common.api.docs import decorators as documentation
from eurydice.common.logging.logger import LOG_KEY, logger


def get_token_response(request: Request) -> Response:
    if isinstance(request.user, AnonymousUser):
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    logger.info({LOG_KEY: "get_token", "username": request.user.username})
    token, created = Token.objects.get_or_create(user=request.user)
    return Response(
        {
            "token": token.key,
        }
    )


@documentation.user_token
class UserTokenView(generics.GenericAPIView):
    def get(self, request: Request) -> Response:
        return get_token_response(request)

    def delete(self, request: Request) -> Response:
        if isinstance(request.user, AnonymousUser):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        request.user.auth_token.delete()
        return get_token_response(request)


__all__ = ("UserTokenView",)
