from pathlib import Path
import os
import sys

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"
# Zmienne ustawione w środowisku serwera jeszcze przed wczytaniem .env —
# zapamiętujemy je do diagnostyki (config/diagnostics.py).
ENV_PRESET_KEYS = sorted(k for k in os.environ if k.startswith(("DB_", "DJANGO_")))
# override=True: .env jest jedynym źródłem konfiguracji na serwerze. Bez tego
# zmienna ustawiona gdzieś w środowisku (np. stare DB_PASSWORD) po cichu
# wygrywała z plikiem i zmiany w .env nie miały żadnego efektu.
load_dotenv(ENV_FILE, override=True)


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


INSECURE_SECRET_KEY = "dev-insecure-key-change-me"
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "").strip() or INSECURE_SECRET_KEY
# Domyślnie produkcja — brak DJANGO_DEBUG w .env nie może włączać trybu
# debug (strony błędów ze szczegółami konfiguracji). Lokalnie .env
# z .env.local.example ustawia DJANGO_DEBUG=True.
DEBUG = env_bool("DJANGO_DEBUG", False)
if not DEBUG and SECRET_KEY == INSECURE_SECRET_KEY:
    # Znany wszystkim klucz = podrabialne ciasteczka (sesja admina,
    # dostęp do arkusza). Lepiej nie wystartować niż działać z nim.
    raise ImproperlyConfigured("Ustaw DJANGO_SECRET_KEY w .env (produkcja, DEBUG=False).")
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
    "django.contrib.sitemaps",
    "tinymce",
    "pages",
    "documents",
    "board",
    "evaluation",
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
    # Polskie znaki zapisujemy wprost (ó zamiast &oacute;).
    "entity_encoding": "raw",
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # Po whitenoise — statyki (style, logo) działają także w trybie serwisowym.
    "config.maintenance.MaintenanceMiddleware",
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
# Django 5.1 nie czyta już STATICFILES_STORAGE — bez STORAGES pliki szły
# pod stałymi adresami (/static/styles.css) i przeglądarki trzymały stary
# CSS po deployu. Manifest dokleja hash do nazwy, więc każda zmiana pliku
# to nowy URL. Testy lecą bez collectstatic (brak manifestu), dlatego
# tam zwykły storage.
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
            if "test" in sys.argv
            else "whitenoise.storage.CompressedManifestStaticFilesStorage"
        )
    },
}

# PDF-y są już skompresowane — gzip nic nie zyskuje, a whitenoise robił
# z każdego dwie dodatkowe kopie .gz (kilkadziesiąt MB przy każdym deployu).
from whitenoise.compress import Compressor  # noqa: E402

WHITENOISE_SKIP_COMPRESS_EXTENSIONS = (*Compressor.SKIP_COMPRESS_EXTENSIONS, "pdf")

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

# Arkusz oceny — podstrona bez linków w menu, dostępna tylko po
# wpisaniu adresu. Ścieżkę można zmienić w .env (np. na trudniejszą do
# zgadnięcia). Wysłane arkusze trafiają do EVALUATION_EMAIL_RECIPIENTS
# (lista po przecinku), domyślnie na adres formularza kontaktowego.
EVALUATION_PATH = os.getenv("EVALUATION_PATH", "arkusz-oceny").strip("/")
EVALUATION_EMAIL_RECIPIENTS = env_list("EVALUATION_EMAIL_RECIPIENTS", [CONTACT_RECIPIENT])
# Kod dostępu do arkusza (przekazywany obserwatorom). Pusty = arkusz
# zamknięty — celowo „fail closed”, żeby zapomniana konfiguracja nie
# otwierała formularza wysyłającego maile z adresu Wydziału.
EVALUATION_ACCESS_CODE = os.getenv("EVALUATION_ACCESS_CODE", "").strip()
# Limity na adres IP w ciągu godziny: wysyłki arkusza i błędne próby kodu.
EVALUATION_SEND_LIMIT = int(os.getenv("EVALUATION_SEND_LIMIT", "5"))
EVALUATION_CODE_ATTEMPT_LIMIT = int(os.getenv("EVALUATION_CODE_ATTEMPT_LIMIT", "10"))
# Limit wiadomości z formularza kontaktowego na adres IP w ciągu godziny.
CONTACT_SEND_LIMIT = int(os.getenv("CONTACT_SEND_LIMIT", "5"))

# Migracje przy starcie aplikacji (config/automigrate.py) — deploy przez FTP
# nie uruchamia `migrate`, a SSH nie zawsze jest dostępne.
AUTO_MIGRATE = env_bool("DJANGO_AUTO_MIGRATE", True)

# Tryb serwisowy: istnienie tego pliku włącza stronę „przerwa techniczna”
# dla wszystkich (wgraj pusty plik przez FTP, usuń, żeby wyłączyć).
MAINTENANCE_FLAG = BASE_DIR / "MAINTENANCE_ON"

# ── Logi błędów do pliku ──────────────────────────────────────────────
# Domyślnie Django przy DEBUG=False nie wypisuje błędów nigdzie (konsola
# działa tylko w trybie debug), więc 500 na produkcji nie zostawiało
# śladu. Zapisujemy je do public_python/logs/django-errors.log — plik da
# się pobrać przez FTP bez dostępu SSH. Katalog nie jest serwowany www.
LOG_DIR = BASE_DIR / "logs"
try:
    LOG_DIR.mkdir(exist_ok=True)
    _file_logging = os.access(LOG_DIR, os.W_OK)
except OSError:
    _file_logging = False

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "{asctime} {levelname} {name}: {message}", "style": "{"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
        **({"file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "django-errors.log",
            "maxBytes": 1024 * 1024,
            "backupCount": 3,
            "encoding": "utf-8",
            "formatter": "verbose",
            "level": "ERROR",
        }} if _file_logging else {}),
        "null": {"class": "logging.NullHandler"},
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"] if _file_logging else ["console"],
            "level": "INFO" if DEBUG else "ERROR",
            # Bez tego wpis szedł też do roota i lądował w pliku dwa razy.
            "propagate": False,
        },
        # Zapytania z obcymi domenami (np. forum.sedziowie.szps.pl) to szum,
        # nie błąd aplikacji — Django i tak odpowiada na nie 400.
        "django.security.DisallowedHost": {"handlers": ["null"], "propagate": False},
    },
    "root": {
        "handlers": ["console", "file"] if _file_logging else ["console"],
        "level": "WARNING",
    },
}

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
