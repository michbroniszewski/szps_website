"""Strona „przerwa techniczna” (503) zamiast błędu 500.

Pokazywana w dwóch sytuacjach:
* ręcznie — gdy w katalogu projektu leży plik MAINTENANCE_ON (wgrany np.
  przez FTP; usunięcie pliku wyłącza tryb, restart nie jest potrzebny),
* automatycznie — gdy nie da się połączyć z bazą danych.

503 + Retry-After mówi wyszukiwarkom, że to chwilowa przerwa, więc nie
usuwają strony z indeksu.
"""

import logging

from django.conf import settings
from django.db import OperationalError
from django.template.loader import render_to_string
from django.http import HttpResponse

log = logging.getLogger(__name__)

RETRY_AFTER = "600"


def maintenance_response():
    response = HttpResponse(render_to_string("errors/maintenance.html"), status=503)
    response["Retry-After"] = RETRY_AFTER
    return response


class MaintenanceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.MAINTENANCE_FLAG.exists():
            return maintenance_response()
        return self.get_response(request)

    def process_exception(self, request, exception):
        if isinstance(exception, OperationalError):
            # Odpowiedź z middleware pomija standardowe logowanie 500 —
            # zapisujemy błąd sami, żeby trafił do logs/django-errors.log.
            log.error("Baza danych niedostępna: %s", request.path, exc_info=exception)
            return maintenance_response()
        return None
