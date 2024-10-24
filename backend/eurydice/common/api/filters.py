from django.db.models.query import QuerySet
from django_filters import rest_framework as filters

from eurydice.common.api.serializers import BytesAsHexadecimalField


def _filter_queryset_by_sha1(queryset: QuerySet, name: str, value: str) -> QuerySet:
    """Take an hexadecimal SHA1, parse it and use it to filter the given queryset."""

    return queryset.filter(**{name: BytesAsHexadecimalField().to_internal_value(value)})


class SHA1Filter(filters.CharFilter):
    """
    A filter that parses SHA1 hashes before searching the queryset.
    """

    def __init__(self, field_name: str) -> None:
        super().__init__(field_name=field_name, method=_filter_queryset_by_sha1)
