"""Entry point dla mydevil.net (Phusion Passenger).

Skrypt zakłada, że aplikacja leży w:
    ~/domains/sedziowie.szps.pl/public_python/
oraz że istnieje virtualenv w:
    ~/domains/sedziowie.szps.pl/public_python/.venv/

Struktura po deployu na mydevil:
    public_python/
    ├── passenger_wsgi.py     <-- ten plik
    ├── manage.py
    ├── config/
    ├── pages/ documents/ board/
    ├── .venv/                <-- virtualenv (nie z repo)
    ├── .env                  <-- konfiguracja (nie z repo)
    └── public/               <-- static + media serwowane przez nginx
"""
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Aktywacja virtualenv — Passenger uruchamia interpreter systemowy,
# musimy sami wskazać wersję z zainstalowanym Django.
VENV_PYTHON = BASE_DIR / ".venv" / "bin" / "python"
if VENV_PYTHON.exists() and sys.executable != str(VENV_PYTHON):
    os.execl(str(VENV_PYTHON), str(VENV_PYTHON), *sys.argv)

sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from django.core.wsgi import get_wsgi_application  # noqa: E402

application = get_wsgi_application()
