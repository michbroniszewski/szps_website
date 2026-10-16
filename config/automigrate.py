"""Automatyczne migracje bazy przy starcie aplikacji.

Na mydevil nie zawsze jest pod ręką SSH, a deploy przez FTP nie uruchamia
`manage.py migrate`. Dlatego passenger_wsgi.py woła `run_pending_migrations()`
przy każdym starcie (Passenger startuje aplikację po deployu / restarcie).

* Migracje uruchamiamy tylko, gdy jakieś czekają — zwykły start to jedno
  szybkie zapytanie o stan tabeli django_migrations.
* Blokada pliku: Passenger może wystartować kilka procesów naraz, a migrować
  ma tylko jeden; pozostałe czekają i widzą już zmigrowaną bazę.
* Błąd (np. niedostępna baza) nie blokuje startu — trafia do
  logs/migrations.log i logs/django-errors.log, a strona pokazuje
  „przerwę techniczną” (config/maintenance.py).

Wyłączenie: DJANGO_AUTO_MIGRATE=False w .env.
"""

import fcntl
import io
import logging
from contextlib import contextmanager
from datetime import datetime

from django.conf import settings
from django.core.management import call_command
from django.db import DEFAULT_DB_ALIAS, connections
from django.db.migrations.executor import MigrationExecutor

log = logging.getLogger(__name__)


def pending_migrations():
    connection = connections[DEFAULT_DB_ALIAS]
    executor = MigrationExecutor(connection)
    targets = executor.loader.graph.leaf_nodes()
    return [migration for migration, _backwards in executor.migration_plan(targets)]


@contextmanager
def _lock():
    settings.LOG_DIR.mkdir(exist_ok=True)
    with open(settings.LOG_DIR / "migrate.lock", "w") as lock_file:
        fcntl.flock(lock_file, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock_file, fcntl.LOCK_UN)


def _write_log(text: str) -> None:
    try:
        settings.LOG_DIR.mkdir(exist_ok=True)
        with open(settings.LOG_DIR / "migrations.log", "a", encoding="utf-8") as f:
            f.write(f"=== {datetime.now():%Y-%m-%d %H:%M:%S} ===\n{text.rstrip()}\n\n")
    except OSError:
        pass


def run_pending_migrations() -> bool:
    """Wykonuje oczekujące migracje. Zwraca True, jeśli coś zmigrowano."""
    if not settings.AUTO_MIGRATE:
        return False
    try:
        with _lock():
            pending = pending_migrations()
            if not pending:
                return False
            names = ", ".join(f"{m.app_label}.{m.name}" for m in pending)
            out = io.StringIO()
            call_command("migrate", interactive=False, verbosity=1, stdout=out, stderr=out)
            _write_log(f"Zastosowano: {names}\n{out.getvalue()}")
            return True
    except Exception as exc:
        log.exception("Automatyczne migracje nie powiodły się")
        _write_log(f"BŁĄD: {type(exc).__name__}: {exc}")
        return False
