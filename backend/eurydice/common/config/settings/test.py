import environ

from eurydice.common.config.settings.base import *
from eurydice.common.config.settings.dev import FAKER_SEED

REMOTE_USER_HEADER_AUTHENTICATION_ENABLED = True

if "django.contrib.auth.backends.RemoteUserBackend" not in AUTHENTICATION_BACKENDS:
    AUTHENTICATION_BACKENDS.append("django.contrib.auth.backends.RemoteUserBackend")

if (
    "rest_framework.authentication.SessionAuthentication"
    not in REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"]
):
    REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"].append(
        "rest_framework.authentication.SessionAuthentication"
    )

REST_FRAMEWORK["TEST_REQUEST_DEFAULT_FORMAT"] = "json"

USER_ASSOCIATION_TOKEN_SECRET_KEY = ""  # nosec

EURYDICE_CONTACT_FR = "contact fr"
UI_BADGE_CONTENT = "ui badge content"
UI_BADGE_COLOR = "ui badge color"
