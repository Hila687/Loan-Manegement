import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def env_list(name: str, default: str = "") -> list[str]:
    return [
        item.strip()
        for item in os.getenv(name, default).split(",")
        if item.strip()
    ]


SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
DEBUG = env_bool("DJANGO_DEBUG", False)

if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "dev-only-change-me-before-production"
    else:
        raise RuntimeError(
            "DJANGO_SECRET_KEY must be set when DJANGO_DEBUG is false"
        )


ALLOWED_HOSTS = env_list(
    "DJANGO_ALLOWED_HOSTS",
    "127.0.0.1,localhost" if DEBUG else "",
)


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "core",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "backend_project.urls"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "backend_project.wsgi.application"


if os.getenv("DATABASE_URL"):
    # Hosting platforms (Render, Railway, Heroku...) give one URL.
    import dj_database_url

    DATABASES = {
        "default": dj_database_url.parse(
            os.environ["DATABASE_URL"],
            conn_max_age=int(os.getenv("DB_CONN_MAX_AGE", "60")),
            conn_health_checks=True,
            ssl_require=env_bool("DB_SSL_REQUIRE", False),
        )
    }
elif os.getenv("DB_ENGINE", "postgresql").lower() == "sqlite":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("DB_NAME", "gemach_db"),
            "USER": os.getenv("DB_USER", "postgres"),
            "PASSWORD": os.getenv("DB_PASSWORD", ""),
            "HOST": os.getenv("DB_HOST", "127.0.0.1"),
            "PORT": os.getenv("DB_PORT", "5432"),
            "CONN_MAX_AGE": int(
                os.getenv(
                    "DB_CONN_MAX_AGE",
                    "60",
                )
            ),
            "OPTIONS": {
                "sslmode": os.getenv(
                    "DB_SSLMODE",
                    "prefer" if DEBUG else "require",
                ),
            },
        }
    }


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME":
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
    },
    {
        "NAME":
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
    },
    {
        "NAME":
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
    },
    {
        "NAME":
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
    },
]


LANGUAGE_CODE = "en-us"
TIME_ZONE = os.getenv(
    "DJANGO_TIME_ZONE",
    "Asia/Jerusalem",
)

USE_I18N = True
USE_TZ = True


STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# The built Vue app (frontend/client/dist). WhiteNoise serves its files at
# the site root (/assets/..., /vite.svg); index.html is served by
# core.spa_views for every page URL.
FRONTEND_DIST = Path(
    os.getenv(
        "FRONTEND_DIST",
        str(BASE_DIR.parent / "frontend" / "client" / "dist"),
    )
)

WHITENOISE_ROOT = FRONTEND_DIST if FRONTEND_DIST.exists() else None


def _immutable_file_test(path, url):
    # Vite puts a content hash in every file under /assets/.
    return url.startswith("/assets/")


WHITENOISE_IMMUTABLE_FILE_TEST = _immutable_file_test

MEDIA_ROOT = Path(
    os.getenv(
        "MEDIA_ROOT",
        str(BASE_DIR / "media"),
    )
)

MEDIA_URL = "/protected-media/"


STORAGES = {
    "default": {
        "BACKEND":
            "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND":
            "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
}


CORS_ALLOWED_ORIGINS = env_list(
    "CORS_ALLOWED_ORIGINS",
    (
        "http://127.0.0.1:5173,"
        "http://localhost:5173"
        if DEBUG
        else ""
    ),
)

CORS_ALLOW_CREDENTIALS = True


CSRF_TRUSTED_ORIGINS = env_list(
    "CSRF_TRUSTED_ORIGINS",
    (
        "http://127.0.0.1:5173,"
        "http://localhost:5173"
        if DEBUG
        else ""
    ),
)


CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SECURE = env_bool("CSRF_COOKIE_SECURE", not DEBUG)

# The site and the API are served from one address, so Lax is enough.
# Set "None" only if the frontend is hosted on a different domain.
CSRF_COOKIE_SAMESITE = os.getenv(
    "CSRF_COOKIE_SAMESITE",
    "Lax",
)


SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = env_bool("SESSION_COOKIE_SECURE", not DEBUG)

SESSION_COOKIE_SAMESITE = os.getenv(
    "SESSION_COOKIE_SAMESITE",
    "Lax",
)

SESSION_COOKIE_AGE = int(
    os.getenv(
        "SESSION_COOKIE_AGE",
        "28800",
    )
)

SESSION_EXPIRE_AT_BROWSER_CLOSE = env_bool(
    "SESSION_EXPIRE_AT_BROWSER_CLOSE",
    not DEBUG,
)

SESSION_SAVE_EVERY_REQUEST = True


SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"


SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https",
)


SECURE_SSL_REDIRECT = env_bool(
    "SECURE_SSL_REDIRECT",
    not DEBUG,
)


SECURE_HSTS_SECONDS = int(
    os.getenv(
        "SECURE_HSTS_SECONDS",
        "3600" if not DEBUG else "0",
    )
)

SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool(
    "SECURE_HSTS_INCLUDE_SUBDOMAINS",
    False,
)

SECURE_HSTS_PRELOAD = env_bool(
    "SECURE_HSTS_PRELOAD",
    False,
)


FILE_UPLOAD_MAX_MEMORY_SIZE = (
    10 * 1024 * 1024
)

DATA_UPLOAD_MAX_MEMORY_SIZE = (
    12 * 1024 * 1024
)

FILE_UPLOAD_PERMISSIONS = 0o600
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o700


# Login-attempt and SMS-code limits live in the cache. In production it is
# a database table shared by all server processes (`createcachetable`).
if env_bool("USE_DB_CACHE", not DEBUG):
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.db.DatabaseCache",
            "LOCATION": "django_cache",
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND":
                "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION":
                "gemach-security-cache",
        }
    }


LOGIN_MAX_ATTEMPTS = int(
    os.getenv(
        "LOGIN_MAX_ATTEMPTS",
        "5",
    )
)

LOGIN_LOCKOUT_SECONDS = int(
    os.getenv(
        "LOGIN_LOCKOUT_SECONDS",
        "900",
    )
)


SIGNED_FORM_MAX_BYTES = int(
    os.getenv(
        "SIGNED_FORM_MAX_BYTES",
        str(10 * 1024 * 1024),
    )
)


TWILIO_ACCOUNT_SID = os.getenv(
    "TWILIO_ACCOUNT_SID",
    "",
)

TWILIO_AUTH_TOKEN = os.getenv(
    "TWILIO_AUTH_TOKEN",
    "",
)

TWILIO_SMS_FROM = os.getenv(
    "TWILIO_SMS_FROM",
    "",
)

TWILIO_WHATSAPP_FROM = os.getenv(
    "TWILIO_WHATSAPP_FROM",
    "",
)

DEFAULT_COUNTRY_CODE = os.getenv(
    "DEFAULT_COUNTRY_CODE",
    "+972",
)

# Sign-in with username, ID number, phone or email
# (see core/auth_backends.py).
AUTHENTICATION_BACKENDS = [
    "core.auth_backends.FlexibleLoginBackend",
]

# Public address of the website, used in the login-details SMS.
SITE_URL = os.getenv(
    "SITE_URL",
    "http://127.0.0.1:5173",
).rstrip("/")

# The public address also tells Django which host name to accept and
# which origin to trust for forms, so one variable is enough to deploy.
if os.getenv("SITE_URL"):
    from urllib.parse import urlparse

    _site = urlparse(SITE_URL)

    if _site.hostname and _site.hostname not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(_site.hostname)

    _origin = f"{_site.scheme}://{_site.netloc}"
    if _origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(_origin)

# Render sets this automatically for its *.onrender.com address.
if os.getenv("RENDER_EXTERNAL_HOSTNAME"):
    ALLOWED_HOSTS.append(os.environ["RENDER_EXTERNAL_HOSTNAME"])
    CSRF_TRUSTED_ORIGINS.append(
        f"https://{os.environ['RENDER_EXTERNAL_HOSTNAME']}"
    )

# One-time SMS code sign-in (core/otp.py)
OTP_TTL_SECONDS = int(os.getenv("OTP_TTL_SECONDS", "600"))
OTP_RESEND_SECONDS = int(os.getenv("OTP_RESEND_SECONDS", "60"))
OTP_MAX_ATTEMPTS = int(os.getenv("OTP_MAX_ATTEMPTS", "5"))
OTP_MAX_CODES_PER_HOUR = int(os.getenv("OTP_MAX_CODES_PER_HOUR", "5"))
OTP_MAX_REQUESTS_PER_IP = int(os.getenv("OTP_MAX_REQUESTS_PER_IP", "20"))

# Email (login codes / account messages). Leave EMAIL_HOST empty in
# development: codes are then shown on screen instead.
EMAIL_HOST = os.getenv("EMAIL_HOST", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", True)
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "no-reply@gemach.local")


# Logs go to stdout, where Docker / the hosting platform collects them.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "plain": {
            "format": "%(asctime)s %(levelname)s %(name)s: %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "plain",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": os.getenv("LOG_LEVEL", "INFO"),
    },
    "loggers": {
        "django.request": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}

# Admins whose email gets server error reports (optional): "Name:a@b.c,..."
ADMINS = [
    tuple(item.split(":", 1))
    for item in env_list("DJANGO_ADMINS")
    if ":" in item
]


# ---- Which messaging channels are switched on -------------------------
# The system works with neither: users then sign in with ID number /
# username + password, and the admin hands out the temporary password.
SMS_ENABLED = bool(
    TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_SMS_FROM
)
EMAIL_ENABLED = bool(EMAIL_HOST)

# Sign-in with a one-time code needs a channel to deliver it. In
# development (DEBUG) the code is shown on screen, so it is always on.
# LOGIN_CODES=off disables it even when SMS / email are configured.
_login_codes = os.getenv("LOGIN_CODES", "auto").strip().lower()
CODE_LOGIN_SMS = _login_codes != "off" and (SMS_ENABLED or DEBUG)
CODE_LOGIN_EMAIL = _login_codes != "off" and (EMAIL_ENABLED or DEBUG)
