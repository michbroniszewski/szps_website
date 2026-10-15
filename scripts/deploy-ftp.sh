#!/usr/bin/env bash
#
# Przyrostowy deploy przez FTP(S) — wysyła tylko pliki, które zmieniły się
# od poprzedniego deployu.
#
# Na serwerze leży `.deploy-manifest` (sha256 + ścieżka każdego wgranego
# pliku). Skrypt liczy ten sam manifest lokalnie, porównuje i wgrywa tylko
# różnice. Porównujemy treść, nie datę modyfikacji: `git checkout` w CI
# ustawia wszystkim plikom bieżącą datę, więc mtime niczego nie mówi.
# Brak manifestu na serwerze (pierwszy raz) albo FULL_DEPLOY=1 = wgranie
# wszystkiego.
#
# Plików usuniętych z repo skrypt nie kasuje na serwerze (tak jak wcześniej
# mirror) — nie przeszkadzają, a usuwanie przez FTP jest ryzykowne.
#
# Uruchamiany z katalogu głównego repo, po `collectstatic`:
#     FTP_HOST=… FTP_USER=… FTP_PASSWORD=… REMOTE_DIR=/public_python \
#         bash scripts/deploy-ftp.sh
#
# Zmienne opcjonalne: FULL_DEPLOY=1, FTP_SSL=0 (tylko do testów lokalnych),
# FTP_PORT, FTP_PARALLEL (domyślnie 4 równoległe transfery).

set -euo pipefail

: "${FTP_HOST:?brak FTP_HOST}" "${FTP_USER:?brak FTP_USER}" "${FTP_PASSWORD:?brak FTP_PASSWORD}"
: "${REMOTE_DIR:?brak REMOTE_DIR}"
FULL_DEPLOY="${FULL_DEPLOY:-0}"
FTP_SSL="${FTP_SSL:-1}"
FTP_PORT="${FTP_PORT:-21}"
FTP_PARALLEL="${FTP_PARALLEL:-4}"
MANIFEST=".deploy-manifest"

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

# ── ustawienia lftp wspólne dla wszystkich połączeń ───────────────────
{
  if [[ "$FTP_SSL" == "1" ]]; then
    echo "set ssl:verify-certificate no"
    echo "set ftp:ssl-force true"
    echo "set ftp:ssl-protect-data true"
  else
    echo "set ftp:ssl-allow no"
  fi
  echo "set ftp:passive-mode true"
  echo "set xfer:clobber on"
  echo "set net:timeout 30"
  echo "set net:max-retries 3"
  echo "set net:reconnect-interval-base 5"
} > "$WORK/settings.lftp"

run_lftp() {
  lftp -p "$FTP_PORT" -u "${FTP_USER},${FTP_PASSWORD}" \
       -e "source $WORK/settings.lftp; source $1" "ftp://${FTP_HOST}"
}

# ── lista plików do wdrożenia ──────────────────────────────────────────
# Pliki śledzone w gicie (bez .env, bazy, venv itp. — tych nie ma w repo)
# minus to, co na serwerze niepotrzebne, plus statyki z collectstatic.
# tmp/restart.txt wgrywamy osobno na końcu.
{
  git ls-files | grep -Ev '^(\.github/|docs/|tmp/|\.env)'
  if [[ -d public/static ]]; then find public/static -type f; fi
} | LC_ALL=C sort -u > "$WORK/files"

while IFS= read -r f; do sha256sum -- "$f"; done < "$WORK/files" > "$MANIFEST"
echo "Pliki w wydaniu: $(wc -l < "$MANIFEST")"

# ── manifest z serwera ─────────────────────────────────────────────────
: > "$WORK/remote-manifest"
if [[ "$FULL_DEPLOY" != "1" ]]; then
  cat > "$WORK/fetch.lftp" <<EOF
set cmd:fail-exit yes
cd "$REMOTE_DIR"
get "$MANIFEST" -o "$WORK/remote-manifest"
bye
EOF
  if ! run_lftp "$WORK/fetch.lftp" >/dev/null 2>&1; then
    echo "Brak manifestu na serwerze — wgrywam wszystko."
    : > "$WORK/remote-manifest"
  fi
else
  echo "FULL_DEPLOY=1 — wgrywam wszystko."
fi

# Linie (hash + ścieżka) obecne lokalnie, a nieobecne na serwerze =
# pliki nowe albo zmienione.
LC_ALL=C comm -23 <(LC_ALL=C sort "$MANIFEST") <(LC_ALL=C sort "$WORK/remote-manifest") \
  | cut -c67- > "$WORK/changed"
echo "Do wysłania: $(wc -l < "$WORK/changed") plików"
head -n 50 "$WORK/changed" | sed 's/^/  + /'
if [[ $(wc -l < "$WORK/changed") -gt 50 ]]; then echo "  … (lista skrócona)"; fi

# ── skrypt wysyłki ─────────────────────────────────────────────────────
mkdir -p tmp
[[ -f tmp/restart.txt ]] || date -u +"%Y-%m-%dT%H:%M:%SZ" > tmp/restart.txt

{
  # Przerwij przy pierwszym błędzie transferu — wtedy manifest na
  # serwerze się nie zmienia i następny deploy wyśle te pliki ponownie.
  echo "set cmd:fail-exit yes"
  echo "cd \"$REMOTE_DIR\""
  if [[ -s "$WORK/changed" ]]; then
    # mput -d tworzy brakujące katalogi; -P = równoległe transfery.
    printf 'mput -d -P %s' "$FTP_PARALLEL"
    while IFS= read -r f; do printf ' "%s"' "${f//\"/\\\"}"; done < "$WORK/changed"
    echo
  fi
  echo "put \"$MANIFEST\" -o \"$MANIFEST\""
  # Restart Passengera na samym końcu, gdy reszta jest już na serwerze.
  # rm + put, żeby zmienił się mtime (Passenger patrzy na mtime).
  echo "set cmd:fail-exit no"
  echo "mkdir -f -p tmp"
  echo "rm tmp/restart.txt"
  echo "put tmp/restart.txt -o tmp/restart.txt"
  echo "rm passenger_wsgi.py"
  echo "put passenger_wsgi.py -o passenger_wsgi.py"
  echo "cls -l tmp/restart.txt passenger_wsgi.py"
  echo "bye"
} > "$WORK/upload.lftp"

run_lftp "$WORK/upload.lftp"
echo "✓ Deploy zakończony."
