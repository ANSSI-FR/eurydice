import datetime
import pathlib

import environ
import humanfriendly
from django.core import exceptions
from django.utils.translation import gettext_lazy as _

from eurydice.common.config.settings.base import (
    ALLOWED_HOSTS,  # noqa
    AUTH_PASSWORD_VALIDATORS,  # noqa
    AUTHENTICATION_BACKENDS,  # noqa
    BASE_DIR,  # noqa
    COMMON_DOCS_PATH,  # noqa
    CSRF_COOKIE_NAME,  # noqa
    CSRF_COOKIE_SAMESITE,  # noqa
    CSRF_COOKIE_SECURE,  # noqa
    CSRF_TRUSTED_ORIGINS,  # noqa
    DATABASES,  # noqa
    DEBUG,  # noqa
    EURYDICE_CONTACT,  # noqa
    EURYDICE_CONTACT_FR,  # noqa
    EURYDICE_VERSION,  # noqa
    INSTALLED_APPS,  # noqa
    LANGUAGE_CODE,  # noqa
    LOGGING,  # noqa
    MAX_PAGE_SIZE,  # noqa
    METADATA_HEADER_PREFIX,  # noqa
    METRICS_SLIDING_WINDOW,  # noqa
    MIDDLEWARE,  # noqa
    PAGE_SIZE,  # noqa
    REMOTE_USER_HEADER,  # noqa
    REMOTE_USER_HEADER_AUTHENTICATION_ENABLED,  # noqa
    REST_FRAMEWORK,  # noqa
    SECRET_KEY,  # noqa
    SECURE_PROXY_SSL_HEADER,  # noqa
    SESSION_COOKIE_AGE,  # noqa
    SESSION_COOKIE_NAME,  # noqa
    SESSION_COOKIE_SAMESITE,  # noqa
    SESSION_COOKIE_SECURE,  # noqa
    SPECTACULAR_SETTINGS,  # noqa
    STATIC_ROOT,  # noqa
    STATIC_URL,  # noqa
    TEMPLATES,  # noqa
    TIME_ZONE,  # noqa
    TRANSFERABLE_MAX_SIZE,  # noqa
    TRANSFERABLE_STORAGE_DIR,  # noqa
    UI_BADGE_COLOR,  # noqa
    UI_BADGE_CONTENT,  # noqa
    USE_I18N,  # noqa
    USE_TZ,  # noqa
    USER_ASSOCIATION_TOKEN_EXPIRES_AFTER,  # noqa
    USER_ASSOCIATION_TOKEN_SECRET_KEY,  # noqa
)

env = environ.Env(
    ORIGIN_CHUNK_SIZE=(str, "10MB"),
    TRANSFERABLE_RANGE_SIZE=(str, "500MB"),
    TRANSFERABLE_HISTORY_DURATION=(str, "5h"),
    TRANSFERABLE_HISTORY_SEND_EVERY=(str, "5min"),
    PACKET_SENDER_QUEUE_SIZE=(int, 1),
    MAX_TRANSFERABLES_PER_PACKET=(int, 800),
    HEARTBEAT_SEND_EVERY=(str, "2min"),
    FILE_REMOVER_EXPIRE_TRANSFERABLES_AFTER=(str, "1day"),
    FILE_REMOVER_RUN_EVERY=(str, "1h"),
    FILE_REMOVER_POLL_EVERY=(str, "200ms"),
    SENDER_POLL_DATABASE_EVERY=(str, "0.1s"),
    SENDER_RANGE_FILLER_CLASS=(str, "UserRotatingTransferableRangeFiller"),
    LIDIS_HOST=(str, None),
    LIDIS_PORT=(int, None),
    DBTRIMMER_TRIM_TRANSFERABLES_AFTER=(str, "1day"),
    DBTRIMMER_RUN_EVERY=(str, "6h"),
    DBTRIMMER_POLL_EVERY=(str, "200ms"),
    FILE_PART_MAIN_SIZE=(int, 5 * 1024 * 1024),
    ENCRYPTION_ENABLED=(bool, False),
    PUBKEY_PATH=(str, "/home/eurydice/keys/eurydice.pub"),
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

# Eurydice

# The size of the chunks to be read from the TRANSFERABLE_RANGE_SIZE
ORIGIN_CHUNK_SIZE = humanfriendly.parse_size(env("ORIGIN_CHUNK_SIZE"), binary=False)

# The size of the TransferableRanges in bytes
# i.e. the size of the file chunks transferred over the wire.
TRANSFERABLE_RANGE_SIZE = humanfriendly.parse_size(env("TRANSFERABLE_RANGE_SIZE"), binary=False)

# Ranges should not be smaller than 5MiB
if TRANSFERABLE_RANGE_SIZE < humanfriendly.parse_size("5MiB"):
    raise exceptions.ImproperlyConfigured(
        f"TRANSFERABLE_RANGE_SIZE must not be smaller than 5MiB"
        f"(currently set to {humanfriendly.format_size(TRANSFERABLE_RANGE_SIZE)})"
    )
# The time range of the history in seconds.
TRANSFERABLE_HISTORY_DURATION = humanfriendly.parse_timespan(env("TRANSFERABLE_HISTORY_DURATION"))

# The sending frequency of the history in seconds.
TRANSFERABLE_HISTORY_SEND_EVERY = humanfriendly.parse_timespan(env("TRANSFERABLE_HISTORY_SEND_EVERY"))

# The duration after which outgoing transferable data is removed and the corresponding
# object in database is marked as EXPIRED.
FILE_REMOVER_EXPIRE_TRANSFERABLES_AFTER = datetime.timedelta(
    seconds=humanfriendly.parse_timespan(env("FILE_REMOVER_EXPIRE_TRANSFERABLES_AFTER"))
)

# How often the file_remover is run.
FILE_REMOVER_RUN_EVERY = datetime.timedelta(seconds=humanfriendly.parse_timespan(env("FILE_REMOVER_RUN_EVERY")))

# How often the file_remover polls for SIGINT.
FILE_REMOVER_POLL_EVERY = datetime.timedelta(seconds=humanfriendly.parse_timespan(env("FILE_REMOVER_POLL_EVERY")))

# Time to wait after having generated all packets
SENDER_POLL_DATABASE_EVERY = humanfriendly.parse_timespan(env("SENDER_POLL_DATABASE_EVERY"))

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
DBTRIMMER_RUN_EVERY = datetime.timedelta(seconds=humanfriendly.parse_timespan(env("DBTRIMMER_RUN_EVERY")))

# How often the dbtrimmer polls for SIGINT.
DBTRIMMER_POLL_EVERY = datetime.timedelta(seconds=humanfriendly.parse_timespan(env("DBTRIMMER_POLL_EVERY")))

# For file parts if encryption is enabled
FILE_PART_MAIN_SIZE = env.str("FILE_PART_MAIN_SIZE")

# Used for encryption/decryption
ENCRYPTION_ENABLED = env("ENCRYPTION_ENABLED")
PUBKEY_PATH = env("PUBKEY_PATH")
