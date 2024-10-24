# type: ignore

from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from django import http
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.db.models import query
from django.utils.translation import gettext_lazy as _
from rest_framework.authtoken import models as token_models

from eurydice.common import enums
from eurydice.common.backoffice import admin as common_admin
from eurydice.origin.api import serializers
from eurydice.origin.core import models

admin.site.site_title = _("Eurydice origin admin")
admin.site.site_header = _("Eurydice origin - Administration")

admin.site.unregister(token_models.TokenProxy)
admin.site.register(token_models.TokenProxy, common_admin.TokenAdmin)


class UserProfileInline(admin.StackedInline):
    model = models.UserProfile
    can_delete = False


@admin.register(models.User)
class UserAdmin(auth_admin.UserAdmin):
    inlines = (UserProfileInline,)
    list_display = auth_admin.UserAdmin.list_display + ("priority", "last_access")

    def get_queryset(self, request: http.HttpRequest) -> query.QuerySet:
        return super().get_queryset(request).select_related("user_profile")

    def priority(self, obj: models.OutgoingTransferable) -> int:
        return obj.user_profile.priority

    priority.short_description = _("Priority")
    priority.admin_order_field = "user_profile__priority"


@admin.register(models.Maintenance)
class MaintenanceAdmin(
    common_admin._DisableAddPermissionMixin,
    common_admin._DisableDeletePermissionMixin,
    admin.ModelAdmin,
):
    fields = ("maintenance",)


class TransferableRangeInline(common_admin.BaseTabularInline):
    model = models.TransferableRange


class TransferableRevocationInline(common_admin.BaseTabularInline):
    model = models.TransferableRevocation


class StateFilter(admin.SimpleListFilter):
    title = "state"
    parameter_name = "state"

    def lookups(
        self, request: http.HttpRequest, model_admin: Any
    ) -> List[Tuple[str, str]]:
        return enums.OutgoingTransferableState.choices

    def queryset(
        self, request: http.HttpRequest, queryset: query.QuerySet
    ) -> query.QuerySet:
        if state := self.value():
            return queryset.filter(state=state)

        return queryset


def _get_help_texts(*field_names: str) -> Dict[str, str]:
    fields = serializers.OutgoingTransferableSerializer().fields
    return {name: fields[name].help_text for name in field_names}


@admin.register(models.OutgoingTransferable)
class OutgoingTransferableAdmin(common_admin.BaseModelAdmin):
    list_display = ("id", "name", "size", "state", "progress", "user", "created_at")
    list_filter = (StateFilter,)
    search_fields = ("id", "name", "state", "user_profile__user__username")

    inlines = (
        TransferableRangeInline,
        TransferableRevocationInline,
    )
    fields = (
        "name",
        "hex_sha1",
        "size",
        "bytes_received",
        "auto_bytes_transferred",
        "user",
        "user_provided_meta",
        "submission_succeeded",
        "submission_succeeded_at",
        "state",
        "progress",
        "created_at",
        "transfer_finished_at",
        "transfer_estimated_finish_date",
        "transfer_speed",
        "transfer_duration",
    )
    help_texts = {
        "hex_sha1": models.OutgoingTransferable.sha1.field.help_text,
        "auto_bytes_transferred": (
            models.OutgoingTransferable.auto_bytes_transferred.field.help_text
        ),
        "user": _("The username of the user owning the transferable"),
        "transfer_duration": _("The duration of the transfer in seconds"),
        **_get_help_texts(
            "submission_succeeded",
            "state",
            "transfer_finished_at",
            "progress",
            "transfer_speed",
            "transfer_estimated_finish_date",
        ),
    }

    def get_queryset(self, request: http.HttpRequest) -> query.QuerySet:
        return super().get_queryset(request).select_related("user_profile__user")

    def hex_sha1(self, obj: models.OutgoingTransferable) -> str:
        return obj.sha1.hex()

    hex_sha1.short_description = _("SHA-1")

    def user(self, obj: models.OutgoingTransferable) -> str:
        return obj.user_profile.user.username

    user.short_description = _("User")
    user.admin_order_field = "user_profile__user__username"

    def state(self, obj: models.OutgoingTransferable) -> str:
        return enums.OutgoingTransferableState(obj.state).label

    state.short_description = _("State")
    state.admin_order_field = "state"

    def transfer_finished_at(self, obj: models.OutgoingTransferable) -> str:
        return common_admin.format_date(obj.transfer_finished_at)

    def progress(self, obj: models.OutgoingTransferable) -> str:
        return obj.progress

    progress.short_description = _("Progress")
    progress.admin_order_field = "progress"

    def transfer_duration(self, obj: models.OutgoingTransferable) -> str:
        return obj.transfer_duration

    def transfer_speed(self, obj: models.OutgoingTransferable) -> str:
        return obj.transfer_speed

    def transfer_estimated_finish_date(self, obj: models.OutgoingTransferable) -> str:
        return obj.transfer_estimated_finish_date
