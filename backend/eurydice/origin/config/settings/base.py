import datetime
import pathlib

import environ
import humanfriendly
from django.core import exceptions
from django.utils.translation import gettext_lazy as _

from eurydice.common.config.settings.base import ALLOWED_HOSTS
from eurydice.common.config.settings.base import AUTH_PASSWORD_VALIDATORS
from eurydice.common.config.settings.base import AUTHENTICATION_BACKENDS
from eurydice.common.config.settings.base import BASE_DIR
from eurydice.common.config.settings.base import COMMON_DOCS_PATH
from eurydice.common.config.settings.base import CSRF_COOKIE_NAME
from eurydice.common.config.settings.base import CSRF_COOKIE_SAMESITE
from eurydice.common.config.settings.base import CSRF_COOKIE_SECURE
from eurydice.common.config.settings.base import CSRF_TRUSTED_ORIGINS
from eurydice.common.config.settings.base import DATABASES
from eurydice.common.config.settings.base import DEBUG
from eurydice.common.config.settings.base import EURYDICE_CONTACT
from eurydice.common.config.settings.base import EURYDICE_CONTACT_FR
from eurydice.common.config.settings.base import EURYDICE_VERSION
from eurydice.common.config.settings.base import INSTALLED_APPS
from eurydice.common.config.settings.base import LANGUAGE_CODE
from eurydice.common.config.settings.base import LOGGING
from eurydice.common.config.settings.base import MAX_PAGE_SIZE
from eurydice.common.config.settings.base import METADATA_HEADER_PREFIX
from eurydice.common.config.settings.base import METRICS_SLIDING_WINDOW
from eurydice.common.config.settings.base import MIDDLEWARE
from eurydice.common.config.settings.base import MINIO_ACCESS_KEY
from eurydice.common.config.settings.base import MINIO_BUCKET_NAME
from eurydice.common.config.settings.base import MINIO_ENABLED
from eurydice.common.config.settings.base import MINIO_ENDPOINT
from eurydice.common.config.settings.base import MINIO_SECRET_KEY
from eurydice.common.config.settings.base import MINIO_SECURE
from eurydice.common.config.settings.base import PAGE_SIZE
from eurydice.common.config.settings.base import REMOTE_USER_HEADER
from eurydice.common.config.settings.base import (
    REMOTE_USER_HEADER_AUTHENTICATION_ENABLED,
)
from eurydice.common.config.settings.base import REST_FRAMEWORK
from eurydice.common.config.settings.base import SECRET_KEY
from eurydice.common.config.settings.base import SECURE_PROXY_SSL_HEADER
from eurydice.common.config.settings.base import SESSION_COOKIE_AGE
from eurydice.common.config.settings.base import SESSION_COOKIE_NAME
from eurydice.common.config.settings.base import SESSION_COOKIE_SAMESITE
from eurydice.common.config.settings.base import SESSION_COOKIE_SECURE
from eurydice.common.config.settings.base import SPECTACULAR_SETTINGS
from eurydice.common.config.settings.base import STATIC_ROOT
from eurydice.common.config.settings.base import STATIC_URL
from eurydice.common.config.settings.base import TEMPLATES
from eurydice.common.config.settings.base import TIME_ZONE
from eurydice.common.config.settings.base import TRANSFERABLE_MAX_SIZE
from eurydice.common.config.settings.base import TRANSFERABLE_STORAGE_DIR
from eurydice.common.config.settings.base import UI_BADGE_COLOR
from eurydice.common.config.settings.base import UI_BADGE_CONTENT
from eurydice.common.config.settings.base import USE_I18N
from eurydice.common.config.settings.base import USE_TZ
from eurydice.common.config.settings.base import USER_ASSOCIATION_TOKEN_EXPIRES_AFTER
from eurydice.common.config.settings.base import USER_ASSOCIATION_TOKEN_SECRET_KEY

env = environ.Env(
    TRANSFERABLE_RANGE_SIZE=(str, "500MB"),
    MULTIPART_PART_SIZE=(int, "5MiB"),  # minio minimum
    TRANSFERABLE_HISTORY_DURATION=(str, "5h"),
    TRANSFERABLE_HISTORY_SEND_EVERY=(str, "5min"),
    PACKET_SENDER_QUEUE_SIZE=(int, 1),
    MAX_TRANSFERABLES_PER_PACKET=(int, 800),
    HEARTBEAT_SEND_EVERY=(str, "2min"),
    SENDER_POLL_DATABASE_EVERY=(str, "0.1s"),
    SENDER_RANGE_FILLER_CLASS=(str, "UserRotatingTransferableRangeFiller"),
    LIDIS_HOST=(str, None),
    LIDIS_PORT=(int, None),
    DBTRIMMER_TRIM_TRANSFERABLES_AFTER=(str, "1day"),
    DBTRIMMER_RUN_EVERY=(str, "6h"),
    DBTRIMMER_POLL_EVERY=(str, "200ms"),
    MINIO_EXPIRATION_DAYS=(int, 8),
)

DOCS_PATH = pathlib.Path(BASE_DIR) / "origin" / "api" / "docs" / "static"

INSTALLED_APPS += [
    "eurydice.origin.core.apps.CoreConfig",
    "eurydice.origin.backoffice.apps.OriginBackofficeConfig",
    "eurydice.origin.api.apps.ApiConfig",
]

ROOT_URLCONF = "eurydice.origin.config.urls"

WSGI_APPLICATION = "eurydice.origin.config.wsgi.application"

AUTH_USER_MODEL = "eurydice_origin_core.User"

# Ideally this would be adjusted per view, but that is not possible
# https://code.djangoproject.com/ticket/32307
# https://docs.djangoproject.com/fr/3.2/ref/settings/#data-upload-max-memory-size
DATA_UPLOAD_MAX_MEMORY_SIZE = TRANSFERABLE_MAX_SIZE

# drf-spectacular
# https://drf-spectacular.readthedocs.io/

SPECTACULAR_SETTINGS["TITLE"] = _("Eurydice origin API")


# Document remote user authentication only if it is enabled
if REMOTE_USER_HEADER_AUTHENTICATION_ENABLED:
    SPECTACULAR_SETTINGS["APPEND_COMPONENTS"]["securitySchemes"]["cookieAuth"] = {
        "type": "apiKey",
        "in": "cookie",
        "name": SESSION_COOKIE_NAME,
        "description": _((DOCS_PATH / "cookie-auth.md").read_text()),
    }
else:
    SPECTACULAR_SETTINGS["APPEND_COMPONENTS"]["securitySchemes"]["basicAuth"] = {
        "type": "http",
        "in": "header",
        "scheme": "basic",
        "description": _((DOCS_PATH / "basic-auth.md").read_text()),
    }

SPECTACULAR_SETTINGS["APPEND_COMPONENTS"]["securitySchemes"]["tokenAuth"] = {
    "type": "apiKey",
    "in": "header",
    "name": "Authorization",
    "description": _((DOCS_PATH / "token-auth.md").read_text()),
}

# S3 Client

# The minio client uploads TransferableRanges in a single threaded multi-part upload
# This determines the size of each minio uploaded part
MULTIPART_PART_SIZE = humanfriendly.parse_size(env("MULTIPART_PART_SIZE"), binary=False)

# Multipart uploads part sizes cannot be smaller than 5MiB in minio
if MULTIPART_PART_SIZE < humanfriendly.parse_size("5MiB"):
    raise exceptions.ImproperlyConfigured(
        f"MULTIPART_PART_SIZE must not be smaller than 5MiB"
        f"(currently set to {humanfriendly.format_size(MULTIPART_PART_SIZE)})"
    )


# Eurydice

# The size of the TransferableRanges in bytes
# i.e. the size of the file chunks transferred over the wire.
TRANSFERABLE_RANGE_SIZE = humanfriendly.parse_size(
    env("TRANSFERABLE_RANGE_SIZE"), binary=False
)

# Objects for multipart uploads cannot be smaller than 5MiB in minio
if TRANSFERABLE_RANGE_SIZE < humanfriendly.parse_size("5MiB"):
    raise exceptions.ImproperlyConfigured(
        f"TRANSFERABLE_RANGE_SIZE must not be smaller than 5MiB"
        f"(currently set to {humanfriendly.format_size(TRANSFERABLE_RANGE_SIZE)})"
    )


# The time range of the history in seconds.
TRANSFERABLE_HISTORY_DURATION = humanfriendly.parse_timespan(
    env("TRANSFERABLE_HISTORY_DURATION")
)

# The sending frequency of the history in seconds.
TRANSFERABLE_HISTORY_SEND_EVERY = humanfriendly.parse_timespan(
    env("TRANSFERABLE_HISTORY_SEND_EVERY")
)

# Time to wait after having generated all packets
SENDER_POLL_DATABASE_EVERY = humanfriendly.parse_timespan(
    env("SENDER_POLL_DATABASE_EVERY")
)

# The class used for implementing TransferableFiller in OnTheWirePacket generator.
SENDER_RANGE_FILLER_CLASS = env("SENDER_RANGE_FILLER_CLASS")

# The sending frequency of an empty heartbeat packet in seconds (if there is no data to send).
HEARTBEAT_SEND_EVERY = humanfriendly.parse_timespan(env("HEARTBEAT_SEND_EVERY"))

# How many packets can be waiting for being sent by the PacketSender.
PACKET_SENDER_QUEUE_SIZE = env("PACKET_SENDER_QUEUE_SIZE")

# How many transferables can coexist in an OnTheWirePacket. Overestimating this value
# can slightly slow down the sender, underestimating this value can disadvantage
# users who send large quantities of small files.
MAX_TRANSFERABLES_PER_PACKET = env("MAX_TRANSFERABLES_PER_PACKET")

# Lidi sender service host.
LIDIS_HOST = env.str("LIDIS_HOST")

# Lidi sender service port.
LIDIS_PORT = env.int("LIDIS_PORT")


# The duration after which transferables are deleted from the database.
DBTRIMMER_TRIM_TRANSFERABLES_AFTER = datetime.timedelta(
    seconds=humanfriendly.parse_timespan(env("DBTRIMMER_TRIM_TRANSFERABLES_AFTER"))
)

# How often the dbtrimmer is run.
DBTRIMMER_RUN_EVERY = datetime.timedelta(
    seconds=humanfriendly.parse_timespan(env("DBTRIMMER_RUN_EVERY"))
)

# How often the dbtrimmer polls for SIGINT.
DBTRIMMER_POLL_EVERY = datetime.timedelta(
    seconds=humanfriendly.parse_timespan(env("DBTRIMMER_POLL_EVERY"))
)

MINIO_EXPIRATION_DAYS = env("MINIO_EXPIRATION_DAYS")
