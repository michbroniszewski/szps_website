"""Prosty limit zdarzeń na adres IP w oknie czasowym (domyślnie godzina)."""

import hashlib
import hmac
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from .models import RateLimitHit

WINDOW = timedelta(hours=1)
# Starsze wpisy nie są już potrzebne do żadnego limitu — sprzątamy je przy okazji.
RETENTION = timedelta(days=1)


def client_ip(request) -> str:
    """Adres klienta. Na mydevil aplikacja stoi za proxy, które DOPISUJE
    adres na końcu X-Forwarded-For — bierzemy więc ostatni wpis (pierwsze
    może podać sam klient, więc nie można im ufać)."""
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",")[-1].strip()
    return request.META.get("REMOTE_ADDR", "")


def _client_key(request) -> str:
    return hmac.new(
        settings.SECRET_KEY.encode(), client_ip(request).encode(), hashlib.sha256
    ).hexdigest()


def is_limited(kind: str, request, limit: int) -> bool:
    since = timezone.now() - WINDOW
    return RateLimitHit.objects.filter(
        kind=kind, client=_client_key(request), created_at__gte=since
    ).count() >= limit


def record(kind: str, request) -> None:
    RateLimitHit.objects.filter(created_at__lt=timezone.now() - RETENTION).delete()
    RateLimitHit.objects.create(kind=kind, client=_client_key(request))
