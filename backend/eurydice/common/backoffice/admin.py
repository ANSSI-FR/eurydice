from datetime import datetime
from typing import Any
from typing import Dict

from django import http
from django.contrib import admin
from django.utils import dateformat
from rest_framework.authtoken import admin as token_admin


class TokenAdmin(token_admin.TokenAdmin):
    search_fields = (
        "key__exact",
        "user__username",
    )


class _DisableChangePermissionMixin:
    def has_change_permission(self, request: http.HttpRequest, obj: Any = None) -> bool:
        return False


class _DisableAddPermissionMixin:
    def has_add_permission(self, request: http.HttpRequest, obj: Any = None) -> bool:
        return False


class _DisableDeletePermissionMixin:
    def has_delete_permission(self, request: http.HttpRequest, obj: Any = None) -> bool:
        return False


class _OrderingMixin:
    ordering = ("-created_at",)


class BaseModelAdmin(  # type: ignore
    _DisableAddPermissionMixin, _OrderingMixin, admin.ModelAdmin
):
    actions = None
    help_texts: Dict[str, str] = {}

    def get_form(self, *args, **kwargs) -> Any:
        kwargs.update({"help_texts": self.help_texts})
        return super().get_form(*args, **kwargs)

    def get_readonly_fields(self, request: http.HttpRequest, obj: Any = None) -> Any:
        if self.fields:
            return self.fields

        return super().get_readonly_fields(request, obj)


class BaseTabularInline(  # type: ignore
    _DisableChangePermissionMixin,
    _DisableAddPermissionMixin,
    _OrderingMixin,
    admin.TabularInline,
):
    extra = 0
    min_num = 0


def format_date(value: datetime) -> str:
    return dateformat.format(value, "j F Y H:i")


__all__ = ("TokenAdmin", "BaseModelAdmin", "BaseTabularInline", "format_date")
