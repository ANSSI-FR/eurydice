# type: ignore

from django import http
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.db.models import query
from django.utils.translation import gettext_lazy as _
from rest_framework.authtoken import models as token_models

from eurydice.common.backoffice import admin as common_admin
from eurydice.destination.api import serializers
from eurydice.destination.core import models

admin.site.site_title = _("Eurydice destination admin")
admin.site.site_header = _("Eurydice destination - Administration")

admin.site.unregister(token_models.TokenProxy)
admin.site.register(token_models.TokenProxy, common_admin.TokenAdmin)


class UserProfileInline(admin.StackedInline):
    model = models.UserProfile
    can_delete = False


@admin.register(models.User)
class UserAdmin(auth_admin.UserAdmin):
    inlines = (UserProfileInline,)
    list_display = auth_admin.UserAdmin.list_display + ("last_access",)


def _get_help_texts(*field_names: str) -> dict[str, str]:
    fields = serializers.IncomingTransferableSerializer().fields
    return {name: fields[name].help_text for name in field_names}


@admin.register(models.IncomingTransferable)
class IncomingTransferableAdmin(common_admin.BaseModelAdmin):
    list_display = ("id", "name", "size", "state", "user", "created_at")
    list_filter = ("state",)
    search_fields = ("id", "name", "state", "user_profile__user__username")

    fields = (
        "name",
        "hex_sha1",
        "size",
        "bytes_received",
        "state",
        "user",
        "user_provided_meta",
        "created_at",
        "finished_at",
        "progress",
        "expires_at",
    )
    help_texts = {
        "hex_sha1": models.IncomingTransferable.sha1.field.help_text,
        "user": _("The username of the user owning the transferable"),
        **_get_help_texts("progress", "expires_at"),
    }

    def get_queryset(self, request: http.HttpRequest) -> query.QuerySet:
        return super().get_queryset(request).select_related("user_profile__user")

    def hex_sha1(self, obj: models.IncomingTransferable) -> str:
        return obj.sha1.hex()

    hex_sha1.short_description = _("SHA-1")

    def user(self, obj: models.IncomingTransferable) -> str:
        if user := obj.user_profile.user:
            return user.username

        return admin.AdminSite.empty_value_display

    user.short_description = _("User")
    user.admin_order_field = "user_profile__user__username"

    def progress(self, obj: models.IncomingTransferable) -> str:
        return obj.progress

    progress.short_description = _("Progress")

    def expires_at(self, obj: models.IncomingTransferable) -> str:
        return obj.expires_at

    expires_at.short_description = _("Expires at")
