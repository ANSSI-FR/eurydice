from typing import Optional
from typing import Type

from drf_spectacular import utils
from rest_framework import exceptions as drf_exceptions
from rest_framework import serializers


def _create_api_exception_serializer(
    exception: Type[drf_exceptions.APIException],
) -> serializers.Serializer:
    """Given a DRF APIException, return a DRF serializer for that exception.

    Args:
        exception: exception to create DRF serializer.

    Returns:
        DRF serializer for the given exception.

    """
    return utils.inline_serializer(
        exception.__name__,
        fields={"detail": serializers.CharField(default=exception.default_detail)},
    )


def create_open_api_response(
    exception: Type[drf_exceptions.APIException], description: Optional[str] = None
) -> utils.OpenApiResponse:
    """Create an OpenApiResponse from a DRF exception.

    Args:
        exception: exception to create the OpenApiResponse from.
        description: optional response description.

    Returns:
        OpenApiResponse for the given exception.

    """
    return utils.OpenApiResponse(
        description=description or exception.default_detail,
        response=_create_api_exception_serializer(exception),
    )


NotFoundResponse = create_open_api_response(drf_exceptions.NotFound)

NotAuthenticatedResponse = create_open_api_response(drf_exceptions.NotAuthenticated)

ValidationErrorResponse = create_open_api_response(drf_exceptions.ValidationError)


__all__ = (
    "create_open_api_response",
    "NotFoundResponse",
    "NotAuthenticatedResponse",
    "ValidationErrorResponse",
)
