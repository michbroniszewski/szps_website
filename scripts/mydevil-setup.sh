#!/usr/bin/env bash
#
# Jednorazowa instalacja aplikacji Django na mydevil.net.
#
# Uruchamiaj z katalogu ~/domains/sedziowie.szps.pl/public_python/ :
#     bash scripts/mydevil-setup.sh
#
# Skrypt jest idempotentny — można go bezpiecznie uruchomić drugi raz;
# przy kolejnych wywołaniach zachowuje się jak update: doinstaluje nowe
# pakiety, wykona brakujące migracje, zebrać statyki, zrestartuje app.
#
# Wymaga: konto na mydevil z powłoką SSH, wgrany kod projektu, plik .env
# z produkcyjną konfiguracją (SECRET_KEY, DEBUG=False, dane PostgreSQL).

set -euo pipefail

# ── ustaw katalog projektu (nadrzędny wobec scripts/) ─────────────────
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_DIR"

echo "==> Projekt: $PROJECT_DIR"

# ── sanity checks ─────────────────────────────────────────────────────
if [[ ! -f requirements.txt ]]; then
  echo "BŁĄD: nie widzę requirements.txt w $PROJECT_DIR" >&2
  exit 1
fi
if [[ ! -f .env ]]; then
  echo "BŁĄD: brak pliku .env w $PROJECT_DIR — utwórz go przed uruchomieniem." >&2
  echo "       (patrz .env.example)" >&2
  exit 1
fi
if [[ ! -f manage.py ]]; then
  echo "BŁĄD: brak manage.py — czy jesteś w katalogu aplikacji?" >&2
  exit 1
fi

# ── wybór interpretera Pythona ─────────────────────────────────────────
PY_BIN=""
for candidate in python3.11 python3.12 python3.10 python3; do
  if command -v "$candidate" >/dev/null 2>&1; then
    PY_BIN="$candidate"
    break
  fi
done
if [[ -z "$PY_BIN" ]]; then
  echo "BŁĄD: nie znalazłem żadnego python3 w PATH." >&2
  exit 1
fi
echo "==> Python: $PY_BIN ($($PY_BIN --version))"

# ── virtualenv ─────────────────────────────────────────────────────────
if [[ ! -d .venv ]]; then
  echo "==> Tworzę virtualenv .venv/"
  "$PY_BIN" -m venv .venv
else
  echo "==> Virtualenv .venv/ już istnieje — pomijam"
fi

# ── instalacja zależności ──────────────────────────────────────────────
echo "==> Aktualizuję pip"
.venv/bin/pip install --upgrade --quiet pip

echo "==> Instaluję pakiety z requirements.txt"
.venv/bin/pip install --quiet -r requirements.txt

# ── migracje ───────────────────────────────────────────────────────────
echo "==> Wykonuję migracje bazy"
.venv/bin/python manage.py migrate --noinput

# ── statyki ────────────────────────────────────────────────────────────
echo "==> Zbieram pliki statyczne do public/static/"
.venv/bin/python manage.py collectstatic --noinput

# ── superuser (jeśli jeszcze nie ma) ───────────────────────────────────
has_superuser=$(.venv/bin/python manage.py shell -c \
  'from django.contrib.auth import get_user_model as g; print(g().objects.filter(is_superuser=True).exists())')

if [[ "$has_superuser" == "True" ]]; then
  echo "==> Superuser już istnieje — pomijam createsuperuser"
else
  echo "==> Tworzę konto administratora (podaj login, e-mail i hasło):"
  .venv/bin/python manage.py createsuperuser
fi

# ── restart Passengera ─────────────────────────────────────────────────
mkdir -p tmp
touch tmp/restart.txt
echo "==> Wysłałem sygnał restartu (tmp/restart.txt)"

echo
echo "✓ Gotowe."
echo "   Sprawdź: https://sedziowie.szps.pl/"
echo "   Panel:   https://sedziowie.szps.pl/admin/"
