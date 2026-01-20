from django_filters import rest_framework as filters

from eurydice.common.api import filters as common_filters
from eurydice.destination.core import models


class IncomingTransferableFilter(filters.FilterSet):
    """
    The set of filters for selecting IncomingTransferables on the destination side.
    """

    created = filters.IsoDateTimeFromToRangeFilter(field_name="created_at")

    finished = filters.IsoDateTimeFromToRangeFilter(field_name="finished_at")

    state = filters.MultipleChoiceFilter(field_name="state", choices=models.IncomingTransferableState.choices)

    name = filters.CharFilter(field_name="name", lookup_expr="icontains")

    sha1 = common_filters.SHA1Filter(field_name="sha1")

    class Meta:
        model = models.IncomingTransferable
        fields = ()
