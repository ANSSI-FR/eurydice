import datetime
import pathlib

import environ
import humanfriendly as hf
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
from eurydice.common.config.settings.base import USER_ASSOCIATION_TOKEN_SECRET_KEY

env = environ.Env(
    PACKET_RECEIVER_HOST=(str, "127.0.0.1"),
    PACKET_RECEIVER_PORT=(int, 65432),
    PACKET_RECEIVER_TIMEOUT=(float, 0.1),
    EXPECT_PACKET_EVERY=(str, "5min"),
    S3REMOVER_EXPIRE_TRANSFERABLES_AFTER=(str, "7days"),
    S3REMOVER_RUN_EVERY=(str, "1min"),
    S3REMOVER_POLL_EVERY=(str, "200ms"),
    DBTRIMMER_TRIM_TRANSFERABLES_AFTER=(str, "14days"),
    DBTRIMMER_RUN_EVERY=(str, "6h"),
    DBTRIMMER_POLL_EVERY=(str, "200ms"),
    RECEIVER_BUFFER_MAX_ITEMS=(int, 4),
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
EXPECT_PACKET_EVERY = datetime.timedelta(
    seconds=hf.parse_timespan(env("EXPECT_PACKET_EVERY"))
)

# The duration after which incoming transferable data is removed and the corresponding
# object in database is marked as EXPIRED.
S3REMOVER_EXPIRE_TRANSFERABLES_AFTER = datetime.timedelta(
    seconds=hf.parse_timespan(env("S3REMOVER_EXPIRE_TRANSFERABLES_AFTER"))
)

# How often the s3remover is run.
S3REMOVER_RUN_EVERY = datetime.timedelta(
    seconds=hf.parse_timespan(env("S3REMOVER_RUN_EVERY"))
)

# How often the s3remover polls for SIGINT.
S3REMOVER_POLL_EVERY = datetime.timedelta(
    seconds=hf.parse_timespan(env("S3REMOVER_POLL_EVERY"))
)

# The duration after which transferables are deleted from the database.
DBTRIMMER_TRIM_TRANSFERABLES_AFTER = datetime.timedelta(
    seconds=hf.parse_timespan(env("DBTRIMMER_TRIM_TRANSFERABLES_AFTER"))
)

# How often the dbtrimmer is run.
DBTRIMMER_RUN_EVERY = datetime.timedelta(
    seconds=hf.parse_timespan(env("DBTRIMMER_RUN_EVERY"))
)

# How often the dbtrimmer polls for SIGINT.
DBTRIMMER_POLL_EVERY = datetime.timedelta(
    seconds=hf.parse_timespan(env("DBTRIMMER_POLL_EVERY"))
)

MINIO_EXPIRATION_DAYS = S3REMOVER_EXPIRE_TRANSFERABLES_AFTER.days + 1
