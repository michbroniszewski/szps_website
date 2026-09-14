#!/usr/bin/env bash
#
# Setup LOKALNEGO środowiska deweloperskiego.
#
# Uruchamiaj z katalogu głównego repo:
#     bash scripts/local-dev-setup.sh
#
# Co robi (idempotentnie — bezpiecznie odpalić drugi raz):
#   * tworzy .venv/ i instaluje zależności z requirements.txt
#   * jeśli nie ma .env, kopiuje .env.local.example i wstrzykuje losowy SECRET_KEY
#   * uruchamia migracje na SQLite (db.sqlite3 w katalogu projektu)
#   * (migracje seedują artykuły oraz skład wydziału z produkcji)
#   * zakłada superusera admin/admin (tylko jeśli jeszcze go nie ma)
#   * odpala management-command `seed_demo_data`, który dodaje przykładowe
#     strony statyczne i kategorie dokumentów do klikania po adminie
#
# Skrypt NIE tyka danych z hostingu — cała zabawa dzieje się na Twoim
# komputerze w db.sqlite3. Baza produkcyjna PostgreSQL na mydevil pozostaje
# nietknięta.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_DIR"

echo "==> Projekt: $PROJECT_DIR"

# ── sanity checks ─────────────────────────────────────────────────────
if [[ ! -f requirements.txt ]]; then
  echo "BŁĄD: nie widzę requirements.txt w $PROJECT_DIR" >&2
  exit 1
fi
if [[ ! -f manage.py ]]; then
  echo "BŁĄD: brak manage.py — czy jesteś w katalogu aplikacji?" >&2
  exit 1
fi

# ── wybór interpretera Pythona ─────────────────────────────────────────
PY_BIN=""
for candidate in python3.12 python3.11 python3.10 python3; do
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
  echo "==> Virtualenv .venv/ już istnieje — pomijam tworzenie"
fi

VENV_PY=".venv/bin/python"
VENV_PIP=".venv/bin/pip"

echo "==> Aktualizuję pip"
"$VENV_PIP" install --upgrade --quiet pip

echo "==> Instaluję pakiety z requirements.txt"
"$VENV_PIP" install --quiet -r requirements.txt

# ── .env dla trybu lokalnego ──────────────────────────────────────────
if [[ ! -f .env ]]; then
  if [[ ! -f .env.local.example ]]; then
    echo "BŁĄD: brak .env.local.example — nie mogę wygenerować .env." >&2
    exit 1
  fi
  echo "==> Tworzę .env na bazie .env.local.example (SQLite, DEBUG=True)"
  cp .env.local.example .env
  # Wstrzykujemy świeży SECRET_KEY, żeby nikt nie startował ze wspólnym.
  SECRET_KEY_VAL="$("$VENV_PY" -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')"
  # Escapowanie na potrzeby sed: bierzemy tylko znaki ASCII, więc /
  # ani & tu nie występują.
  "$VENV_PY" - "$SECRET_KEY_VAL" <<'PY'
import pathlib, sys
key = sys.argv[1]
p = pathlib.Path(".env")
text = p.read_text()
text = text.replace("zamien-mnie-na-losowy-ciag-znakow", key)
p.write_text(text)
PY
  echo "    wygenerowałem świeży DJANGO_SECRET_KEY"
else
  echo "==> .env już istnieje — nie ruszam (zachowuję Twoje ustawienia)"
fi

# ── ostrzeżenie, jeśli .env wskazuje bazę produkcyjną ────────────────
if grep -q '^DB_ENGINE=postgresql' .env; then
  cat >&2 <<'WARN'

⚠️  UWAGA: Twój .env ma DB_ENGINE=postgresql — to ustawienie PRODUKCYJNE.
    Ten skrypt służy do lokalnego testowania i zaraz uruchomi migracje na
    bazie z .env. Jeśli nie chcesz łączyć się z produkcją, ustaw
    DB_ENGINE=sqlite (albo skasuj .env i uruchom skrypt ponownie, żeby
    wygenerował świeży lokalny .env).
    Przerywam — daję Ci szansę zdecydować.

WARN
  exit 1
fi

# ── migracje ───────────────────────────────────────────────────────────
echo "==> Uruchamiam migracje (SQLite → db.sqlite3)"
"$VENV_PY" manage.py migrate --noinput

# ── superuser admin/admin (tylko lokalnie!) ───────────────────────────
echo "==> Sprawdzam konto administratora"
"$VENV_PY" manage.py shell <<'PY'
from django.contrib.auth import get_user_model

User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(
        username="admin",
        email="admin@example.local",
        password="admin",
    )
    print("    utworzyłem superusera admin / admin (zmień hasło w /admin/)")
else:
    print("    superuser już istnieje — pomijam")
PY

# ── seed przykładowych treści redakcyjnych ────────────────────────────
echo "==> Dodaję przykładowe strony statyczne i kategorie dokumentów"
"$VENV_PY" manage.py seed_demo_data

cat <<'DONE'

✓ Gotowe. Środowisko lokalne czeka na Ciebie.

  Uruchom serwer deweloperski:
      bash scripts/local-dev-run.sh
  albo ręcznie:
      .venv/bin/python manage.py runserver

  Strona:  http://127.0.0.1:8000/
  Panel:   http://127.0.0.1:8000/admin/   (login: admin / hasło: admin)

  Baza:    db.sqlite3 (SQLite, lokalny plik)
  Media:   public/media/  (uploady z admina lądują tu)

  Skrypt jest idempotentny — możesz go odpalić drugi raz np. po
  `pip install`, migracji, albo żeby zresetować przykładowe strony
  statyczne (seed_demo_data używa update_or_create).

DONE
