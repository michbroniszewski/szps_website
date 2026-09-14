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

## Dokumentacja

- [`docs/local-testing.md`](docs/local-testing.md) — lokalne środowisko dev.
- [`docs/deployment-mydevil.md`](docs/deployment-mydevil.md) — pierwszy setup na hostingu.
- [`docs/github-actions-deploy.md`](docs/github-actions-deploy.md) — automatyczny deploy przez `git push main`.
