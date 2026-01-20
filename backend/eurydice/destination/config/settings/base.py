import datetime
import pathlib

import environ
import humanfriendly as hf
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
    REMOTE_USER_HEADER_AUTHENTICATION_ENABLED,
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
    USER_ASSOCIATION_TOKEN_SECRET_KEY,  # noqa
)

env = environ.Env(
    PACKET_RECEIVER_HOST=(str, "127.0.0.1"),
    PACKET_RECEIVER_PORT=(int, 65432),
    PACKET_RECEIVER_TIMEOUT=(float, 0.1),
    EXPECT_PACKET_EVERY=(str, "5min"),
    FILE_REMOVER_EXPIRE_TRANSFERABLES_AFTER=(str, "7days"),
    FILE_REMOVER_RUN_EVERY=(str, "1min"),
    FILE_REMOVER_POLL_EVERY=(str, "200ms"),
    DBTRIMMER_TRIM_TRANSFERABLES_AFTER=(str, "14days"),
    DBTRIMMER_RUN_EVERY=(str, "6h"),
    DBTRIMMER_POLL_EVERY=(str, "200ms"),
    RECEIVER_BUFFER_MAX_ITEMS=(int, 4),
    PRIVKEY_PATH=(str, "/home/eurydice/keys/eurydice"),
)

DOCS_PATH = pathlib.Path(BASE_DIR) / "destination" / "api" / "docs" / "static"

INSTALLED_APPS += [
    "eurydice.destination.core.apps.CoreConfig",
    "eurydice.destination.backoffice.apps.DestinationBackofficeConfig",
    "eurydice.destination.api.apps.ApiConfig",
]

ROOT_URLCONF = "eurydice.destination.config.urls"

WSGI_APPLICATION = "eurydice.destination.config.wsgi.application"

AUTH_USER_MODEL = "eurydice_destination_core.User"

# drf-spectacular
# https://drf-spectacular.readthedocs.io/

SPECTACULAR_SETTINGS["TITLE"] = _("Eurydice destination API")

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

# The TCP server of the packet receiver is bound to this host address.
PACKET_RECEIVER_HOST = env("PACKET_RECEIVER_HOST")

# The TCP server of the packet receiver is bound to this port.
PACKET_RECEIVER_PORT = env("PACKET_RECEIVER_PORT")

# The duration (in seconds) after which the packet receiver timeout while waiting for
# new packets. This interrupt is needed to process received Unix signals and log
# missed heartbeats.
PACKET_RECEIVER_TIMEOUT = env("PACKET_RECEIVER_TIMEOUT")

# How many Transferables the receiver can store in its buffer queue before dropping
# them. If the receiver receives data faster than it can process (ie. sender is faster
# than receiver) then its queue would keep increasing in size, and eventually run out
# of memory. This limit prevents that. The receiver will log an error when it has to
# drop a Transferable because of this limit.
RECEIVER_BUFFER_MAX_ITEMS = env("RECEIVER_BUFFER_MAX_ITEMS")

# The receiver will log an error if it does not receive a packet in this time interval.
EXPECT_PACKET_EVERY = datetime.timedelta(seconds=hf.parse_timespan(env("EXPECT_PACKET_EVERY")))

# The duration after which incoming transferable data is removed and the corresponding
# object in database is marked as EXPIRED.
FILE_REMOVER_EXPIRE_TRANSFERABLES_AFTER = datetime.timedelta(
    seconds=hf.parse_timespan(env("FILE_REMOVER_EXPIRE_TRANSFERABLES_AFTER"))
)

# How often the file_remover is run.
FILE_REMOVER_RUN_EVERY = datetime.timedelta(seconds=hf.parse_timespan(env("FILE_REMOVER_RUN_EVERY")))

# How often the file_remover polls for SIGINT.
FILE_REMOVER_POLL_EVERY = datetime.timedelta(seconds=hf.parse_timespan(env("FILE_REMOVER_POLL_EVERY")))

# The duration after which transferables are deleted from the database.
DBTRIMMER_TRIM_TRANSFERABLES_AFTER = datetime.timedelta(
    seconds=hf.parse_timespan(env("DBTRIMMER_TRIM_TRANSFERABLES_AFTER"))
)

# How often the dbtrimmer is run.
DBTRIMMER_RUN_EVERY = datetime.timedelta(seconds=hf.parse_timespan(env("DBTRIMMER_RUN_EVERY")))

# How often the dbtrimmer polls for SIGINT.
DBTRIMMER_POLL_EVERY = datetime.timedelta(seconds=hf.parse_timespan(env("DBTRIMMER_POLL_EVERY")))

# Internal path to private key
PRIVKEY_PATH = env("PRIVKEY_PATH")
