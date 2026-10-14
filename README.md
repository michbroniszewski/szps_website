# szps_website

Strona Wydziału Sędziowskiego ŚZPS ([sedziowie.szps.pl](https://sedziowie.szps.pl/)).
Django 5.1 + PostgreSQL na mydevil.net (produkcja) / SQLite lokalnie.

## Szybki start — lokalne testowanie

Jedno polecenie stawia całe środowisko (venv, migracje, superuser
`admin/admin`, przykładowe treści):

```bash
bash scripts/local-dev-setup.sh
bash scripts/local-dev-run.sh
```

Serwer: http://127.0.0.1:8000/, panel: http://127.0.0.1:8000/admin/

Szczegóły i pełen flow „lokalny test → deploy": [`docs/local-testing.md`](docs/local-testing.md).

## Arkusz oceny (podstrona ukryta)

`/arkusz-oceny/` — formularz obserwatora do oceny jednego sędziego (na bazie wzoru WZPS 2017) z
generowaniem PDF. Nie ma linków w menu ani w sitemap, strona wysyła
`noindex`. Treść arkusza: `evaluation/sheet.py`; PDF: `evaluation/pdf.py`.
Ścieżkę i adresatów wysyłki e-mail ustawia się w `.env`
(`EVALUATION_PATH`, `EVALUATION_EMAIL_RECIPIENTS` — patrz `.env.example`;
domyślnie wysyłka idzie na `CONTACT_RECIPIENT`).

Zabezpieczenia arkusza: **kod dostępu** (`EVALUATION_ACCESS_CODE` — bez
niego arkusz jest zamknięty; lokalnie `test`), pole-pułapka na boty oraz
limity na adres IP: 5 wysyłek i 10 błędnych kodów na godzinę
(`EVALUATION_SEND_LIMIT`, `EVALUATION_CODE_ATTEMPT_LIMIT`). Liczniki są
w bazie (model `RateLimitHit`, IP zapisywane tylko jako skrót HMAC).

Plik HTML do przeglądu poza stroną (np. do rozesłania członkom Wydziału):

```bash
.venv/bin/python manage.py export_evaluation_html -o arkusz-oceny-podglad.html
```

## Prywatność

- Fonty (Archivo, Barlow) są hostowane lokalnie w `static/fonts/` (OFL) —
  strona nie łączy się z Google Fonts ani innymi serwisami zewnętrznymi.
- Polityka prywatności to strona statyczna `polityka-prywatnosci`
  (`/s/polityka-prywatnosci/`), zakładana przez migrację jako szkic.
  Po uzupełnieniu fragmentów [DO UZUPEŁNIENIA] i zaznaczeniu „Opublikowana”
  w panelu link pojawia się w stopce i przy zgodzie w formularzu kontaktowym.
  Zalogowani redaktorzy widzą szkice stron statycznych przed publikacją.

## Dokumentacja

- [`docs/local-testing.md`](docs/local-testing.md) — lokalne środowisko dev.
- [`docs/deployment-mydevil.md`](docs/deployment-mydevil.md) — pierwszy setup na hostingu.
- [`docs/github-actions-deploy.md`](docs/github-actions-deploy.md) — automatyczny deploy przez `git push main`.
