# Deploy na mydevil.net

Instrukcja od zera — jak postawić projekt Django na mydevil.

## Wymagania po stronie hostingu

- Domena `sedziowie.szps.pl` skonfigurowana jako **PythonSite** w panelu mydevil (już jest).
- Baza PostgreSQL utworzona (już jest).
- Dostęp SFTP do katalogu `~/domains/sedziowie.szps.pl/public_python/`.

## Struktura docelowa na serwerze

```
~/domains/sedziowie.szps.pl/public_python/
├── passenger_wsgi.py        (z repo)
├── manage.py                (z repo)
├── config/, pages/, ...     (z repo)
├── static/, templates/      (z repo)
├── .venv/                   (utworzony na serwerze, NIE z repo)
├── .env                     (utworzony na serwerze, NIE z repo)
├── public/                  (już istnieje — tu ląduje static i media)
│   ├── static/
│   └── media/
└── tmp/                     (już istnieje — mechanizm restartu Passengera)
```

## 1. Wgraj kod na serwer

Wgraj przez SFTP zawartość repo do `public_python/`, **z pominięciem** katalogów:
- `.git/`, `.venv/`, `db.sqlite3`, `.env`
- (opcjonalnie na start) `assets/`, `dokumenty/`, `uploads/`, `screenshots/` — te są ze starej wersji statycznej, docelowo będą wgrywane przez panel admina.

Wgraj **do samego `public_python/`**, nie do `public_python/public/`.

## 2. Utwórz virtualenv i zainstaluj zależności

Docelowo trzeba to zrobić przez SSH — a Ty masz konto FTP-only. Dwie ścieżki:

**A. Poproś administratora konta głównego** o wykonanie w katalogu `public_python/`:

```bash
python3.11 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt
```

**B. Ewentualnie użyj crona w panelu mydevil** do jednorazowego uruchomienia
tych komend (mydevil pozwala uruchomić polecenie shellowe jako cron „przy
najbliższej minucie" — po pierwszym uruchomieniu wyłącz).

## 3. Skonfiguruj `.env`

Utwórz przez SFTP plik `public_python/.env`:

```
DJANGO_SECRET_KEY=<wygenerowany 50-znakowy klucz>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=sedziowie.szps.pl,www.sedziowie.szps.pl

DB_ENGINE=postgresql
DB_NAME=<nazwa bazy>
DB_USER=<user bazy>
DB_PASSWORD=<hasło do bazy>
DB_HOST=pgsqlXX.mydevil.net
DB_PORT=5432
```

Sekretny klucz wygenerujesz lokalnie:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## 4. Migracje bazy i static

Także przez SSH / cron:

```bash
cd ~/domains/sedziowie.szps.pl/public_python
.venv/bin/python manage.py migrate
.venv/bin/python manage.py collectstatic --noinput
.venv/bin/python manage.py createsuperuser  # tylko raz — konto admina
```

`collectstatic` skopiuje pliki statyczne do `public/static/`, skąd nginx
serwuje je bezpośrednio (bez uruchamiania Pythona) — szybko.

## 5. Restart aplikacji

Po każdej zmianie kodu:

```bash
touch ~/domains/sedziowie.szps.pl/public_python/tmp/restart.txt
```

Bez SSH: przez SFTP zmień datę modyfikacji pliku `tmp/restart.txt` (albo
usuń i wgraj pusty).

## 6. Sprawdź

- `https://sedziowie.szps.pl/` — strona główna
- `https://sedziowie.szps.pl/admin/` — panel administracyjny (login = superuser z kroku 4)

## Kolejne wdrożenia (rutyna)

1. `git pull` w `public_python/` (jeśli masz Gita na serwerze), lub SFTP na zmienione pliki.
2. Migracje: `.venv/bin/python manage.py migrate` (jeśli zmieniły się modele).
3. Static: `.venv/bin/python manage.py collectstatic --noinput` (jeśli zmieniły się CSS/JS/obrazki).
4. Restart: `touch tmp/restart.txt`.

## Logi

Logi Passengera i błędy Django znajdziesz w:

```
~/domains/sedziowie.szps.pl/logs/
```

Podglądaj: `tail -f ~/domains/sedziowie.szps.pl/logs/error.log`
