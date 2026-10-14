"""Kod dostępu do arkusza: sprawdzenie i zapamiętanie w podpisanym ciasteczku."""

import hashlib
import hmac

from django.conf import settings

COOKIE = "ev_access"
SALT = "evaluation.access"
MAX_AGE = 60 * 60 * 24 * 180  # 180 dni — obserwator wpisuje kod raz na sezon


def _fingerprint() -> str:
    # W ciasteczku nie ma samego kodu, tylko jego skrót — po zmianie kodu
    # w .env wszystkie wcześniejsze dostępy przestają działać.
    return hashlib.sha256(settings.EVALUATION_ACCESS_CODE.encode()).hexdigest()[:32]


def is_configured() -> bool:
    return bool(settings.EVALUATION_ACCESS_CODE)


def code_matches(code: str) -> bool:
    return is_configured() and hmac.compare_digest(
        code.strip().encode(), settings.EVALUATION_ACCESS_CODE.encode()
    )


def has_access(request) -> bool:
    if not is_configured():
        return False
    value = request.get_signed_cookie(COOKIE, default=None, salt=SALT, max_age=MAX_AGE)
    return value is not None and hmac.compare_digest(value, _fingerprint())


def grant(response) -> None:
    response.set_signed_cookie(
        COOKIE, _fingerprint(), salt=SALT, max_age=MAX_AGE,
        httponly=True, samesite="Lax", secure=not settings.DEBUG,
    )
