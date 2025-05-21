import pathlib
from os import path

import django.core.exceptions
import environ
import humanfriendly
from django.utils.translation import gettext_lazy as _

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1", "api"]),
    CSRF_TRUSTED_ORIGINS=(list, []),
    SECRET_KEY=(str, "thxdd#i*^!nt-1s_md@q-&"),
    MINIO_ENABLED=(bool, True),
    MINIO_SECURE=(bool, False),
    MINIO_BUCKET_NAME=(str, "eurydice"),
    MINIO_ENDPOINT=(str, ""),
    MINIO_ACCESS_KEY=(str, ""),
    MINIO_SECRET_KEY=(str, ""),
    TRANSFERABLE_STORAGE_DIR=(str, "/home/eurydice/data"),
    # This value should be kept in sync with the TRANSFERABLE_MAX_SIZE
    # constant defined in the frontend/src/origin/constants.js file
    TRANSFERABLE_MAX_SIZE=(str, "50TiB"),
    LOG_FORMAT=(str, "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
    LOG_LEVEL=(str, "INFO"),
    LOG_TO_FILE=(bool, False),
    USER_ASSOCIATION_TOKEN_EXPIRES_AFTER=(str, "15min"),
    METRICS_SLIDING_WINDOW=(str, "60min"),
    REMOTE_USER_HEADER_AUTHENTICATION_ENABLED=(bool, False),
    REMOTE_USER_HEADER=(str, "HTTP_X_REMOTE_USER"),
    EURYDICE_VERSION=(str, "development"),
    SECURE_COOKIES=(bool, True),
    SAMESITE_COOKIES=(str, "Strict"),
    SESSION_COOKIE_AGE=(str, "24h"),
    PAGE_SIZE=(int, 50),
    MAX_PAGE_SIZE=(int, 100),
    THROTTLE_RATE=(str, "30/second"),
    EURYDICE_API=(str, ""),
    EURYDICE_CONTACT=(str, ""),
    EURYDICE_CONTACT_FR=(str, ""),
    UI_BADGE_CONTENT=(str, "default badge value"),
    UI_BADGE_COLOR=(str, "#01426a"),
)

DEBUG = env("DEBUG")

BASE_DIR = path.dirname(
    path.dirname(path.dirname(path.dirname(path.abspath(__file__))))
)

COMMON_DOCS_PATH = pathlib.Path(BASE_DIR) / "common" / "api" / "docs" / "static"

SECRET_KEY = env("SECRET_KEY")

ALLOWED_HOSTS = env("ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = env("CSRF_TRUSTED_ORIGINS")

# The version number for this release of the eurydice application
EURYDICE_VERSION = env("EURYDICE_VERSION")

# Contact information for support
EURYDICE_CONTACT = env("EURYDICE_CONTACT")

# https://docs.djangoproject.com/fr/3.2/ref/settings/#append-slash
APPEND_SLASH = True

# Tell django to trust X-Forwarded-Proto header sent by reverse proxy to determine user's protocol
# https://docs.djangoproject.com/fr/3.2/ref/settings/#secure-proxy-ssl-header
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

INSTALLED_APPS = [
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "rest_framework",
    "rest_framework.authtoken",
    "django_filters",
    "drf_spectacular",
    "eurydice.common.redoc.apps.ReDocConfig",
    "eurydice.common.permissions.apps.PermissionsConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "eurydice.common.api.middlewares.AuthenticatedUserHeaderMiddleware",
    "eurydice.common.api.middlewares.LastAccessMiddleware",
]

AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend"]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            path.join(BASE_DIR, "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

OPTIONS = {"context_processors"}

# Session configuration
# https://docs.djangoproject.com/en/3.2/ref/settings/#id15

# https://docs.djangoproject.com/en/3.2/ref/settings/#session-cookie-age
SESSION_COOKIE_AGE = humanfriendly.parse_timespan(env("SESSION_COOKIE_AGE"))

# https://docs.djangoproject.com/fr/3.2/ref/settings/#session-cookie-secure
SESSION_COOKIE_SECURE = env("SECURE_COOKIES")

# https://docs.djangoproject.com/en/3.2/ref/settings/#session-cookie-samesite
SESSION_COOKIE_SAMESITE = env("SAMESITE_COOKIES")

# https://docs.djangoproject.com/en/3.2/ref/settings/#session-cookie-name
SESSION_COOKIE_NAME = "eurydice_sessionid"

# CSRF configuration

# https://docs.djangoproject.com/en/3.2/ref/settings/#csrf-cookie-name
CSRF_COOKIE_NAME = "eurydice_csrftoken"

# https://docs.djangoproject.com/en/3.2/ref/settings/#csrf-cookie-samesite
CSRF_COOKIE_SAMESITE = env("SAMESITE_COOKIES")

# https://docs.djangoproject.com/en/3.2/ref/settings/#csrf-cookie-secure
CSRF_COOKIE_SECURE = env("SECURE_COOKIES")

# Pagination

PAGE_SIZE = env("PAGE_SIZE")
MAX_PAGE_SIZE = env("MAX_PAGE_SIZE")

# Throttling

THROTTLE_RATE = env("THROTTLE_RATE")

# DRF

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": PAGE_SIZE,
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_THROTTLE_RATES": {"create_transferable": THROTTLE_RATE},
}

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST"),
        "PORT": env("DB_PORT"),
        "ATOMIC_REQUESTS": True,
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",  # noqa: E501
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Remote authentication
# https://docs.djangoproject.com/en/3.2/howto/auth-remote-user/
# https://www.django-rest-framework.org/api-guide/authentication/#remoteuserauthentication

REMOTE_USER_HEADER_AUTHENTICATION_ENABLED = env(
    "REMOTE_USER_HEADER_AUTHENTICATION_ENABLED"
)

REMOTE_USER_HEADER = env("REMOTE_USER_HEADER")

if REMOTE_USER_HEADER_AUTHENTICATION_ENABLED:
    AUTHENTICATION_BACKENDS.append("django.contrib.auth.backends.RemoteUserBackend")
    REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"].append(
        "rest_framework.authentication.SessionAuthentication"
    )
else:
    # BasicAuthentication needs to be on top so that django replies with
    # `WWW-Authenticate: Basic` instead of `WWW-Authenticate: Token`
    # along with a 401
    REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"].insert(
        0, "rest_framework.authentication.BasicAuthentication"
    )


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "fr-FR"

TIME_ZONE = "Europe/Paris"

USE_I18N = False

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = path.join(BASE_DIR, "staticfiles")

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    }
}

# Logging
# https://docs.djangoproject.com/en/3.2/topics/logging/

LOGGING_EURYDICE_HANDLERS = [
    "default",
]
LOG_TO_FILE = env("LOG_TO_FILE")
if LOG_TO_FILE:
    LOGGING_EURYDICE_HANDLERS.append("file")

LOGGING = {
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"},
        "require_debug_true": {"()": "django.utils.log.RequireDebugTrue"},
    },
    "formatters": {
        "default": {"format": env("LOG_FORMAT")},
        "json": {
            "class": "eurydice.common.logging.JSONFormatter",
        },
    },
    "handlers": {
        "default": {
            "level": "DEBUG",
            "formatter": "default",
            "class": "logging.StreamHandler",
        },
        # django debug logs are only logged when DEBUG is True
        "django_console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "filters": ["require_debug_true"],
            "level": "DEBUG",
        },
        # django requests are always logged
        "django.server": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": "DEBUG",
        },
    },
    "loggers": {
        "django": {
            "handlers": LOGGING_EURYDICE_HANDLERS,
            "level": env("LOG_LEVEL"),
        },
        # django requests log
        "django.server": {
            "handlers": LOGGING_EURYDICE_HANDLERS,
            "level": env("LOG_LEVEL"),
            "propagate": False,
        },
        "eurydice": {
            "handlers": LOGGING_EURYDICE_HANDLERS,
            "level": env("LOG_LEVEL"),
        },
    },
    "version": 1,
}

if LOG_TO_FILE:
    LOGGING["handlers"]["file"] = {
        "class": "logging.handlers.RotatingFileHandler",
        "filename": pathlib.Path("/") / "var" / "log" / "app" / "log.json",
        "formatter": "json",
        "maxBytes": 1024 * 1024 * 15,  # 15MB
        "backupCount": 10,
        "level": "DEBUG",
    }

# Minio

MINIO_ENDPOINT = env.str("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = env.str("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = env.str("MINIO_SECRET_KEY")
MINIO_SECURE = env("MINIO_SECURE")
MINIO_BUCKET_NAME = env("MINIO_BUCKET_NAME")
MINIO_ENABLED = env("MINIO_ENABLED")
# Following setting is overridden in destination and origin settings
MINIO_EXPIRATION_DAYS = 9

# If minio is disabled, use filesystem
TRANSFERABLE_STORAGE_DIR = env.str("TRANSFERABLE_STORAGE_DIR")

if MINIO_ENABLED:
    if not MINIO_ENDPOINT:
        raise django.core.exceptions.ImproperlyConfigured(
            "The MINIO_ENDPOINT environment variable must not be empty"
        )
else:
    if not TRANSFERABLE_STORAGE_DIR:
        raise django.core.exceptions.ImproperlyConfigured(
            "The TRANSFERABLE_STORAGE_DIR environment variable must not be empty"
        )

# drf-spectacular
# https://drf-spectacular.readthedocs.io/

SPECTACULAR_SETTINGS = {
    "POSTPROCESSING_HOOKS": [
        "eurydice.common.api.docs.custom_spectacular.postprocessing_hook"
    ],
    "VERSION": "v1",
    "APPEND_COMPONENTS": {
        "securitySchemes": {},
    },
    "TAGS": [
        {
            "name": "OpenApi3 documentation",
            "description": _((COMMON_DOCS_PATH / "openapi.md").read_text()),
        },
        {
            "name": "Transferring files",
            "description": _((COMMON_DOCS_PATH / "transferring-files.md").read_text()),
        },
        {
            "name": "Account management",
            "description": _((COMMON_DOCS_PATH / "account-management.md").read_text()),
        },
    ],
}


SPECTACULAR_SETTINGS["DESCRIPTION"] = (
    (COMMON_DOCS_PATH / "welcome.md")
    .read_text()
    .format(
        EURYDICE_API=env("EURYDICE_API").upper(),
        EURYDICE_HOST=ALLOWED_HOSTS[0],
        EURYDICE_VERSION=EURYDICE_VERSION,
        EURYDICE_CONTACT=EURYDICE_CONTACT,
    )
)

# Eurydice

# The maximum size in bytes of a Transferable i.e. a file submitted to be transferred.
# The limit value of this parameter is set by Minio
# https://docs.min.io/docs/minio-server-limits-per-tenant.html.
TRANSFERABLE_MAX_SIZE = humanfriendly.parse_size(
    env("TRANSFERABLE_MAX_SIZE"), binary=False
)

METADATA_HEADER_PREFIX = "Metadata-"

USER_ASSOCIATION_TOKEN_SECRET_KEY = env.str("USER_ASSOCIATION_TOKEN_SECRET_KEY")
USER_ASSOCIATION_TOKEN_EXPIRES_AFTER = humanfriendly.parse_timespan(
    env("USER_ASSOCIATION_TOKEN_EXPIRES_AFTER")
)

METRICS_SLIDING_WINDOW = humanfriendly.parse_timespan(env("METRICS_SLIDING_WINDOW"))

EURYDICE_CONTACT_FR = env("EURYDICE_CONTACT_FR")

UI_BADGE_CONTENT = env("UI_BADGE_CONTENT")
UI_BADGE_COLOR = env("UI_BADGE_COLOR")
