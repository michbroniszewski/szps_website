# Deploy na mydevil.net

## Sytuacja wyjściowa

- Domena `sedziowie.szps.pl` skonfigurowana jako **PythonSite** w panelu mydevil.
- Baza PostgreSQL utworzona — masz dane: host, nazwa bazy, user, hasło.
- Dostęp SFTP (konto `f1448_sedziowie` na `s70.mydevil.net`) do katalogu
  `~/public_python/`.
- Dostęp SSH tylko przez konto główne mydevil (lub przez administratora
  konta głównego).

## Struktura docelowa na serwerze

```
~/public_python/
├── passenger_wsgi.py        (z repo)
├── manage.py                (z repo)
├── config/, pages/, board/, documents/, templates/, static/  (z repo)
├── scripts/mydevil-setup.sh (z repo — jednorazowy setup)
├── .venv/                   (utworzony przez setup, NIE z repo)
├── .env                     (utworzony przez Ciebie, NIE z repo)
├── public/                  (już istnieje — tu ląduje static i media)
│   ├── static/              (wypełnia collectstatic)
│   └── media/               (upload z panelu admina)
└── tmp/                     (mechanizm restartu Passengera)
```

## Kolejność działań

### 0. Przygotowanie `.env` (Ty, lokalnie)

Wygeneruj `SECRET_KEY`:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Utwórz lokalnie plik `.env` (skopiuj z `.env.example` i uzupełnij):
```
DJANGO_SECRET_KEY=<wklej wygenerowany klucz — długi ciąg znaków>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=sedziowie.szps.pl,www.sedziowie.szps.pl

DB_ENGINE=postgresql
DB_NAME=<nazwa bazy z zamówienia>
DB_USER=<user bazy z zamówienia>
DB_PASSWORD=<hasło do bazy>
DB_HOST=<host bazy, np. pgsql4.mydevil.net>
DB_PORT=5432
```

**Nie commituj tego pliku** — jest w `.gitignore`.

### 1. Upload przez SFTP (Ty, ~10 min)

Wgraj **całą zawartość repo** do `~/public_python/`,
z pominięciem:
- `.git/`
- `.venv/`
- `db.sqlite3`
- `__pycache__/`
- `.env.example`
- `uploads/`, `screenshots/`, `z_orig.png`, `.thumbnail` (stare rzeczy, nie
  używane przez Django)

Plus **wgraj lokalnie utworzony `.env`** do tego samego katalogu.

W FileZilla filtry uploadu (Ustawienia → Filtry katalogów) — dodaj wyżej
wymienione wzorce.

Cel: `public_python/passenger_wsgi.py`, `public_python/manage.py`,
`public_python/.env`, `public_python/scripts/mydevil-setup.sh` istnieją na
serwerze po zakończeniu uploadu.

### 2. Jedna komenda administratora (~3 min)

Wyślij osobie z dostępem SSH:

> W katalogu `~/public_python/` wgrałem kod
> Django. Wejdź SSH i uruchom:
> ```
> cd ~/public_python && bash scripts/mydevil-setup.sh
> ```
> Skrypt zapyta o login/e-mail/hasło do konta administratora panelu — podaj
> mi je po fakcie (albo ustaw dowolne i przekaż mi hasło do zmiany).

Co zrobi skrypt:
- utworzy virtualenv w `.venv/`
- zainstaluje pakiety z `requirements.txt`
- wykona migracje (utworzy tabele w PostgreSQL)
- zbierze pliki statyczne do `public/static/`
- utworzy konto superusera (jeśli jeszcze nie ma)
- zrestartuje Passengera przez `touch tmp/restart.txt`

Skrypt jest **idempotentny** — bezpiecznie można go uruchomić drugi raz.

### 3. Weryfikacja (Ty)

- `https://sedziowie.szps.pl/` — strona główna
- `https://sedziowie.szps.pl/admin/` — panel administracyjny (zaloguj się
  danymi superusera z kroku 2)
- Dodaj testową aktualność w adminie, sprawdź że pojawia się na stronie
  głównej

## Kolejne wdrożenia (po pierwszym setupie)

**Zmiany w plikach (HTML, CSS, JS, template, kod widoku):**
- wgraj zmienione pliki przez SFTP
- zrestartuj: przez SFTP zmień datę modyfikacji pliku
  `public_python/tmp/restart.txt` (w FileZilla: prawy klik → Właściwości)

**Zmiany wymagające migracji bazy (nowe/zmienione modele):**
- wgraj pliki + nowe migracje
- poproś administratora o uruchomienie `bash scripts/mydevil-setup.sh` —
  skrypt idempotentnie wykona `migrate` + `collectstatic` + restart

**Nowe pakiety w `requirements.txt`:**
- wgraj `requirements.txt`
- poproś administratora o `bash scripts/mydevil-setup.sh`

## Automatyzacja kolejnych deployów

Po pierwszym setupie kolejne wdrożenia idą automatycznie przez GitHub
Actions — patrz [`github-actions-deploy.md`](./github-actions-deploy.md).
Krótko: dodajesz dwa sekrety (`MYDEVIL_FTP_USER`, `MYDEVIL_FTP_PASSWORD`)
w GitHubie i `git push main` deploy'uje same. Migracje bazy i nowe pakiety
pip nadal wymagają uruchomienia `scripts/mydevil-setup.sh` przez admina.

## Logi

Błędy Django i Passengera:
```
~/domains/sedziowie.szps.pl/logs/error.log
```

Podgląd na żywo (admin, przez SSH):
```
tail -f ~/domains/sedziowie.szps.pl/logs/error.log
```
