# Lokalne testowanie zmian

Ten branch (i ten dokument) daje szybką pętlę „zmiana → sprawdzenie na
swoim komputerze → dopiero potem push na produkcję" — bez łączenia się
z bazą PostgreSQL na mydevil.

## Co dokładnie robi tryb lokalny

- Używa **SQLite** (`db.sqlite3` w katalogu projektu) zamiast Postgresa.
  Baza produkcyjna na mydevil pozostaje **nietknięta**.
- Ma `DJANGO_DEBUG=True` — Django pokazuje pełne stack-trace'y i serwuje
  pliki `MEDIA` / `STATIC` bez pomocy nginxa.
- Automatycznie zakłada superusera `admin` / `admin` (tylko lokalnie!).
- Migracje seedują artykuły i skład wydziału (te same wpisy, co na
  produkcji — patrz `pages/migrations/0003_seed_initial_articles.py`
  i `board/migrations/0002_seed_initial_members.py`).
- Komenda `seed_demo_data` dodaje kilka przykładowych stron statycznych
  i kategorii dokumentów (z prefiksem `demo-`), żeby było co klikać
  w adminie.

Plik `.env`, `db.sqlite3` i katalog `public/` są w `.gitignore` — nie
wpadną przypadkiem do commita.

## Pierwsze uruchomienie (2 minuty)

Z katalogu głównego repo:

```bash
bash scripts/local-dev-setup.sh
```

Skrypt:

1. tworzy `.venv/` i instaluje pakiety z `requirements.txt`,
2. generuje `.env` na bazie `.env.local.example` ze świeżym
   `DJANGO_SECRET_KEY` (jeśli plik jeszcze nie istnieje),
3. uruchamia migracje na SQLite,
4. zakłada superusera `admin` / `admin` (tylko jeśli jeszcze go nie ma),
5. odpala `python manage.py seed_demo_data`.

Skrypt jest **idempotentny** — można go uruchomić drugi raz po
`pip install`, po nowej migracji albo żeby zresetować demo-strony.

## Codzienna pętla

Uruchom serwer:

```bash
bash scripts/local-dev-run.sh
# lub jawnie:
.venv/bin/python manage.py runserver
```

Otwórz:

- Strona:   http://127.0.0.1:8000/
- Panel:    http://127.0.0.1:8000/admin/  (login `admin` / hasło `admin`)

Testowa pętla po zmianach w kodzie:

```bash
# 1) sprawdź, że baza jest w zgodzie z modelami
.venv/bin/python manage.py makemigrations
.venv/bin/python manage.py migrate

# 2) uruchom serwer i przeklikaj zmiany
bash scripts/local-dev-run.sh

# 3) gdy jest OK — dopiero wtedy commit + push na main
git add -A
git commit -m "..."
git push origin main   # deploy uruchomi się przez GitHub Actions
```

## Reset środowiska (od zera)

Zaczyna się od czystej bazy i świeżych treści demo:

```bash
rm -f db.sqlite3
bash scripts/local-dev-setup.sh
```

Reset tylko treści demo (bez ruszania artykułów/składu wydziału z migracji):

```bash
.venv/bin/python manage.py seed_demo_data --reset
```

Reset virtualenva (np. po zmianie wersji Pythona):

```bash
rm -rf .venv
bash scripts/local-dev-setup.sh
```

## Bezpieczniki: co odróżnia lokalny setup od produkcji

- **Baza**: `.env.local.example` ma `DB_ENGINE=sqlite` bez żadnych danych
  do Postgresa. Jeśli podmienisz na `postgresql`, `local-dev-setup.sh`
  **przerwie działanie** z ostrzeżeniem, żebyś nie odpalił migracji na
  hostingu przez pomyłkę.
- **SECRET_KEY**: skrypt generuje losowy dla każdego świeżego `.env`
  (nie wysyłamy go do repo).
- **Superuser `admin/admin`**: powstaje tylko przy pustej bazie. Nie
  wgrywaj tego pliku bazy na serwer.
- **`.env`, `db.sqlite3`, `public/`, `.venv/`**: w `.gitignore`, GitHub
  Actions deploy też ich nie wysyła (patrz sekcja „Co jest wgrywane"
  w [github-actions-deploy.md](./github-actions-deploy.md)).

## Testowanie nowych rzeczy przed deployem

Sensowny flow, gdy dłubiesz coś ryzykowniejszego (nowy model, zmiana
templatów, przebudowa view'a):

1. **Odgałęź** się od `main` do brancha roboczego:
   `git checkout -b feature/nowe-cos`.
2. **Zmieniaj** kod, sprawdzaj lokalnie
   (`scripts/local-dev-run.sh`) — masz cały admin do klikania.
3. Jeśli dodałeś model, zrób migrację i sprawdź ją lokalnie:
   `manage.py makemigrations && manage.py migrate`.
   Włącz też migrację odwrotną: `manage.py migrate <app> <poprzednia_migracja>` —
   powinna przejść bez błędu (świadczy o poprawnym `RunPython(..., reverse)`
   albo brakującym `AddField` z `null=True`).
4. Gdy jest dobrze — **push do brancha roboczego** i otwórz PR (nie push
   od razu na `main`, bo `main` deployuje się automatycznie).
5. Po code review — merge do `main`. GitHub Actions wgra zmiany na
   `sedziowie.szps.pl`.
6. Jeśli PR zawiera **nowy model / nową migrację / nowy pakiet w
   `requirements.txt`** — po deployu poproś admina o
   `bash scripts/mydevil-setup.sh` (skrypt idempotentnie zrobi
   `migrate` + `pip install` + restart Passengera).

Dla samych zmian HTML/CSS/JS krok 6 nie jest potrzebny — deploy sam
odświeży Passengera.
