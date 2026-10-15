#!/usr/bin/env bash
#
# Jednorazowa instalacja aplikacji Django na mydevil.net.
#
# Uruchamiaj z katalogu ~/public_python/ :
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
VENV_PY=".venv/bin/python"

# Katalog .venv/ może istnieć, ale być uszkodzony (np. po przerwanej
# instalacji) — wtedy tworzymy go od nowa.
if [[ -d .venv ]] && ! "$VENV_PY" -c 'import sys' >/dev/null 2>&1; then
  echo "==> Virtualenv .venv/ jest uszkodzony — tworzę go od nowa"
  rm -rf .venv
fi

if [[ ! -d .venv ]]; then
  echo "==> Tworzę virtualenv .venv/"
  "$PY_BIN" -m venv .venv
else
  echo "==> Virtualenv .venv/ już istnieje — pomijam"
fi
echo "==> Python w venv: $("$VENV_PY" --version)"

# ── instalacja zależności ──────────────────────────────────────────────
# WAŻNE: na mydevil launcher .venv/bin/pip potrafi zwrócić
# „Permission denied”, choć .venv/bin/python działa. Dlatego pip wołamy
# ZAWSZE przez interpreter: .venv/bin/python -m pip. Nie zmieniać na
# .venv/bin/pip.
VENV_PIP=("$VENV_PY" -m pip)

echo "==> Aktualizuję pip"
"${VENV_PIP[@]}" install --upgrade --quiet pip

echo "==> Instaluję pakiety z requirements.txt"
"${VENV_PIP[@]}" install --quiet -r requirements.txt

# ── migracje ───────────────────────────────────────────────────────────
echo "==> Wykonuję migracje bazy"
"$VENV_PY" manage.py migrate --noinput

# ── statyki ────────────────────────────────────────────────────────────
# Ostrzeżenia „Found another file with the destination path
# 'admin/js/...'” są oczekiwane (nakładanie się statyk Django admin
# i django-unfold) i nie blokują wdrożenia — liczy się kod wyjścia.
echo "==> Zbieram pliki statyczne do public/static/"
echo "    (ostrzeżenia „Found another file … admin/js/…” są niegroźne)"
"$VENV_PY" manage.py collectstatic --noinput

# ── superuser (jeśli jeszcze nie ma) ───────────────────────────────────
has_superuser=$("$VENV_PY" manage.py shell -c \
  'from django.contrib.auth import get_user_model as g; print(g().objects.filter(is_superuser=True).exists())')

if [[ "$has_superuser" == "True" ]]; then
  echo "==> Superuser już istnieje — pomijam createsuperuser"
else
  echo "==> Tworzę konto administratora (podaj login, e-mail i hasło):"
  "$VENV_PY" manage.py createsuperuser
fi

# ── restart Passengera ─────────────────────────────────────────────────
mkdir -p tmp
touch tmp/restart.txt
echo "==> Wysłałem sygnał restartu (tmp/restart.txt)"

echo
echo "✓ Gotowe."
echo "   Sprawdź: https://sedziowie.szps.pl/"
echo "   Panel:   https://sedziowie.szps.pl/admin/"
