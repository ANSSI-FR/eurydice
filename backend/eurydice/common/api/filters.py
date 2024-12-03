from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy as _
from django_filters import rest_framework as filters
from rest_framework import status
from rest_framework.exceptions import APIException

from eurydice.common.api.serializers import BytesAsHexadecimalField


class InvalidQueryParameterError(APIException):
    """Exception raised when the DBTrimmer removed a page that was being explored."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid query parameter."
    default_code = "bad_request"

    # mypy does not recognize qualname
    # https://github.com/python/mypy/issues/6473
    default_code = __qualname__

    def __init__(self, field: str):
        super().__init__(detail=_(f"field {field} malformed."))


def _filter_queryset_by_sha1(queryset: QuerySet, name: str, value: str) -> QuerySet:
    """Take an hexadecimal SHA1, parse it and use it to filter the given queryset."""

    try:
        serialized_value = BytesAsHexadecimalField().to_internal_value(value)
    except ValueError:
        raise InvalidQueryParameterError("sha1")
    return queryset.filter(**{name: serialized_value})


class SHA1Filter(filters.CharFilter):
    """
    A filter that parses SHA1 hashes before searching the queryset.
    """

    def __init__(self, field_name: str) -> None:
        super().__init__(field_name=field_name, method=_filter_queryset_by_sha1)
