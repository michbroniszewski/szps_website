# Automatyczny deploy przez GitHub Actions

Po pierwszym uruchomieniu Django na mydevil (przez `scripts/mydevil-setup.sh`)
każdą kolejną zmianę w kodzie/HTML/CSS wypuszczasz przez `git push` — reszta
dzieje się sama.

## Jak to działa

Workflow `.github/workflows/deploy.yml` uruchamia się:
- automatycznie po **każdym pushu do gałęzi `main`**,
- ręcznie z zakładki **Actions → Deploy to mydevil → Run workflow** (przydatne
  do pierwszego testu i do wymuszenia deployu bez pushu).

Co robi:
1. Pobiera kod z repo.
2. Instaluje Django lokalnie w środowisku CI.
3. Uruchamia `collectstatic` — kompresowane wersje `.gz` i `.br` plików
   statycznych powstają w GitHubie, nie na serwerze.
4. Aktualizuje `tmp/restart.txt` datą deployu i skrótem SHA — po wgraniu
   Passenger widzi zmienioną datę i przeładowuje aplikację.
5. Wgrywa **tylko zmienione pliki** przez FTPS (śledzone przez plik
   `.ftp-deploy-sync-state.json` na serwerze).

## Konfiguracja jednorazowa

### 1. Dodaj sekrety w repozytorium GitHub

Wejdź na `https://github.com/michbroniszewski/szps_website/settings/secrets/actions`
i dodaj dwa **Repository secrets**:

| Nazwa | Wartość |
|---|---|
| `MYDEVIL_FTP_USER` | `f1448_sedziowie` |
| `MYDEVIL_FTP_PASSWORD` | Hasło do konta FTP |

Sekrety są zaszyfrowane i **niewidoczne** nawet dla Ciebie po zapisaniu —
GitHub pokazuje tylko nazwy.

### 2. (opcjonalnie) Ustaw zmienną z hostem FTP

Jeśli Twój serwer to nie `s70.mydevil.net`, dodaj **Repository variable**
(nie secret — to nie tajemnica) o nazwie `MYDEVIL_FTP_HOST` z odpowiednim
hostem (np. `s71.mydevil.net`). Domyślnie workflow używa `s70.mydevil.net`.

## Pierwsze uruchomienie

**Zanim wypchniesz workflow do `main`**, przetestuj go z gałęzi feature:

1. Zmerguj (albo wypchnij) `.github/workflows/deploy.yml` na dowolną gałąź.
2. Wejdź do zakładki **Actions** w GitHubie.
3. Wybierz workflow **Deploy to mydevil**.
4. Kliknij **Run workflow** → wybierz gałąź → **Run**.
5. Śledź logi — powinny skończyć się „Deployment complete" po ~1-2 minutach.

Sprawdź na serwerze przez SFTP, czy zmieniły się daty modyfikacji plików
i czy pojawił się plik `.ftp-deploy-sync-state.json`.

Wejdź na `https://sedziowie.szps.pl/` — jeśli widzisz najnowszą wersję,
działa.

## Co jest wgrywane, a co nie

Wgrywane:
- Cały kod Django (`config/`, `pages/`, `board/`, `documents/`)
- Szablony i statyki (`templates/`, `static/`, `public/static/` — po
  `collectstatic`)
- `manage.py`, `passenger_wsgi.py`, `requirements.txt`
- `scripts/` (skrypt setupowy przydatny przy `migrate`)
- `tmp/restart.txt` (spust restartu — wgrywany na końcu)

Pomijane (nie tykają serwera):
- `.git/`, `.github/`, `.venv/`, `__pycache__/`
- `.env` (na serwerze masz swój — deploy go **nie nadpisze**)
- `db.sqlite3` (lokalny plik dev)
- `public/media/**` — **uploadowane przez adminów zdjęcia i pliki są
  chronione**, deploy ich nie skasuje
- `uploads/`, `screenshots/`, `z_orig.png`, `.thumbnail` (śmieci ze starej
  wersji statycznej)
- `docs/`, `node_modules/`, `.DS_Store`

## Co deploy **nie** robi

**Nie uruchamia migracji bazy.** Dane logowania do Postgresa nie są w CI
(świadomie — jedno miejsce mniej gdzie może wyciec). Więc po dodaniu
nowego modelu lub zmianie pola w istniejącym musisz poprosić admina o:

```bash
cd ~/domains/sedziowie.szps.pl/public_python && bash scripts/mydevil-setup.sh
```

Skrypt jest idempotentny — bezpiecznie wykona `pip install` (jeśli
`requirements.txt` się zmienił), `migrate` i restart.

**Nie instaluje nowych pakietów pip.** Ta sama zasada — nowe zależności
wymagają `mydevil-setup.sh` u admina.

## Diagnostyka błędów

**„530 Login incorrect"** — złe dane w sekretach. Sprawdź `MYDEVIL_FTP_USER`
i `MYDEVIL_FTP_PASSWORD` w Settings → Secrets.

**„550 Failed to change directory"** — zła ścieżka `server-dir` w workflow.
Sprawdź czy `./domains/sedziowie.szps.pl/public_python/` odpowiada temu,
co widzisz po zalogowaniu przez FTP.

**Strona po deployu wygląda jak przed** — Passenger nie zauważył restartu.
Sprawdź czy `tmp/restart.txt` faktycznie wylądował (przez FTP zobacz datę).
Jeśli tak, poproś admina o `touch tmp/restart.txt` z powłoki.

**Django zwraca 500 po deployu** — najpewniej brakująca migracja albo
nowy pakiet. Log w `~/domains/sedziowie.szps.pl/logs/error.log`. Poproś
admina o `bash scripts/mydevil-setup.sh` żeby uzupełnić.

**Deploy zniszczył plik `.env`** — nie powinien, jest w exclude. Ale
jeśli tak — na serwerze utwórz plik `.env` ponownie z wartościami z etapu 0
w `deployment-mydevil.md`.

## Automatyczny flow docelowy

```
zmiana w kodzie/HTML/CSS/PDF
        ↓
   git commit + push (do main)
        ↓
   GitHub Actions uruchamia się (~1-2 min)
        ↓
   collectstatic w CI → FTPS upload zmienionych plików → tmp/restart.txt
        ↓
   Passenger się restartuje, nowa wersja online
```

Zmiana wymagająca migracji lub nowego pakietu — dodatkowo:
```
        ↓
   wiadomość do admina + `bash scripts/mydevil-setup.sh` na serwerze
```
