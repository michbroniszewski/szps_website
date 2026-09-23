#!/usr/bin/env bash
#
# Uruchom lokalny serwer deweloperski Django.
#
# Zakłada, że setup został już wykonany:
#     bash scripts/local-dev-setup.sh
#
# Domyślnie nasłuchuje na 127.0.0.1:8000. Zmień port/host:
#     bash scripts/local-dev-run.sh 0.0.0.0:8080

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_DIR"

if [[ ! -x .venv/bin/python ]]; then
  echo "BŁĄD: brak .venv/. Uruchom najpierw:" >&2
  echo "    bash scripts/local-dev-setup.sh" >&2
  exit 1
fi

ADDR="${1:-127.0.0.1:8000}"

echo "==> Serwer: http://${ADDR}/"
echo "==> Panel:  http://${ADDR}/admin/"
echo "==> Ctrl+C żeby zatrzymać."
echo
exec .venv/bin/python manage.py runserver "$ADDR"
