from pathlib import Path
import os

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def env_bool(name: str, default: bool) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "on"}


def env_list(name: str, default: list[str]) -> list[str]:
    val = os.getenv(name)
    if not val:
        return default
    return [item.strip() for item in val.split(",") if item.strip()]


SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-insecure-key-change-me")
DEBUG = env_bool("DJANGO_DEBUG", True)
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", ["localhost", "127.0.0.1"])

CSRF_TRUSTED_ORIGINS = [
    f"https://{host}" for host in ALLOWED_HOSTS if host not in {"localhost", "127.0.0.1"}
]

INSTALLED_APPS = [
    # django-unfold — musi być PRZED django.contrib.admin, żeby jego
    # szablony admina wygrały w resolverze.
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "tinymce",
    "pages",
    "documents",
    "board",
]

# Branding + kolory dla django-unfold. Wszystko opcjonalne — jak
# usuniesz ten słownik, dostajesz domyślny motyw unfold.
UNFOLD = {
    "SITE_TITLE": "Panel ŚZPS",
    "SITE_HEADER": "Wydział Sędziowski ŚZPS",
    "SITE_SUBHEADER": "Zarządzanie treścią strony",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
}

# Domyślna konfiguracja edytora TinyMCE. Redaktor dostaje pasek
# narzędzi z podstawowym formatowaniem, listami, linkami i tabelami —
# bez wtyczek serwerowych, bez API-key (używamy wersji GPL).
TINYMCE_DEFAULT_CONFIG = {
    "height": 400,
    "menubar": "edit view insert format tools table",
    "plugins": (
        "advlist autolink lists link image charmap preview anchor "
        "searchreplace visualblocks code fullscreen insertdatetime "
        "media table code help wordcount"
    ),
    "toolbar": (
        "undo redo | formatselect | bold italic underline | "
        "alignleft aligncenter alignright alignjustify | "
        "bullist numlist outdent indent | link table image | "
        "removeformat | code | help"
    ),
    "language": "pl",
    "branding": False,
    "promotion": False,
    "convert_urls": False,
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

if os.getenv("DB_ENGINE", "sqlite").lower() == "postgresql":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("DB_NAME", ""),
            "USER": os.getenv("DB_USER", ""),
            "PASSWORD": os.getenv("DB_PASSWORD", ""),
            "HOST": os.getenv("DB_HOST", ""),
            "PORT": os.getenv("DB_PORT", "5432"),
            "CONN_MAX_AGE": 60,
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "pl"
TIME_ZONE = "Europe/Warsaw"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "public" / "static"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "public" / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ── E-mail (formularz kontaktowy) ────────────────────────────────────
# Backend domyślnie SMTP na produkcji, `console` na dev — tam nic nie
# leci na zewnątrz, wiadomość wypisuje się w logu runservera.
EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend" if DEBUG
    else "django.core.mail.backends.smtp.EmailBackend",
)
EMAIL_HOST = os.getenv("EMAIL_HOST", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", True)
EMAIL_USE_SSL = env_bool("EMAIL_USE_SSL", False)
EMAIL_TIMEOUT = 15

# From: nagłówek, adresat formularza — konfigurowalne osobno, bo na
# mydevil mailbox uwierzytelnienia (EMAIL_HOST_USER) to często ten sam
# adres co „ws@szps.pl", ale nie musi.
DEFAULT_FROM_EMAIL = os.getenv("DJANGO_FROM_EMAIL", "Formularz ŚZPS <ws@szps.pl>")
CONTACT_RECIPIENT = os.getenv("CONTACT_RECIPIENT", "ws@szps.pl")

if not DEBUG:
    # Passenger na mydevil siedzi za nginx-em, który terminuje SSL.
    # Bez tej pary Django nie wie, że request przyszedł HTTPS-em i
    # request.is_secure() jest False → cookies bez `secure`, przekierowanie
    # w pętlę itp.
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

    # Cookies tylko po HTTPS.
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # Przekieruj HTTP → HTTPS na poziomie Django (dodatkowo do reguł nginx).
    # Env override potrzebny do testów — Django Client jedzie po http://
    # i przy SSL redirect dostaje 301 na każdą stronę.
    SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL_REDIRECT", True)

    # HSTS: 180 dni + subdomeny + preload. Preload wymaga jednorazowego
    # zgłoszenia domeny do https://hstspreload.org, ale sam nagłówek jest
    # bezpieczny i sensowny.
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 180
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Ogólne utwardzenia — nie kosztują nic, a `manage.py check --deploy`
    # przestaje na nie krzyczeć.
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = "same-origin"
    X_FRAME_OPTIONS = "DENY"
