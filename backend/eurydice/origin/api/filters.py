from django_filters import rest_framework as filters

from eurydice.common import enums
from eurydice.common.api import filters as common_filters
from eurydice.origin.core import models


class OutgoingTransferableFilter(filters.FilterSet):
    """
    The set of filters for selecting OutgoingTransferables on the origin side.
    """

    created = filters.IsoDateTimeFromToRangeFilter(field_name="created_at")

    submission_succeeded = filters.IsoDateTimeFromToRangeFilter(
        field_name="submission_succeeded_at"
    )

    transfer_finished = filters.IsoDateTimeFromToRangeFilter(field_name="finished_at")

    state = filters.MultipleChoiceFilter(
        field_name="state", choices=enums.OutgoingTransferableState.choices
    )

    name = filters.CharFilter(field_name="name", lookup_expr="icontains")

    sha1 = common_filters.SHA1Filter(field_name="sha1")

    class Meta:
        model = models.OutgoingTransferable
        fields = ()
