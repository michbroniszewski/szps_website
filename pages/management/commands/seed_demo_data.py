"""Idempotentny seed danych do lokalnego testowania.

Uzupełnia zawartość, której NIE wypełniają migracje produkcyjne:
przykładowe strony statyczne (o Wydziale, kontakt, regulamin). Wpisy nie
kolidują z produkcją — wszystko chodzi po ``update_or_create`` na
slugach z prefiksem ``demo-``, więc można spokojnie odpalić komendę
wielokrotnie oraz — jeśli seed przypadkiem trafi na produkcję —
usunąć wpisy filtrując po ``slug__startswith='demo-'``.

Kategorie dokumentów są teraz seedowane migracją
``documents/0003_seed_initial_documents`` (kanoniczne 4 kategorie
z produkcji), więc ta komenda ich już nie tworzy, żeby nie nadpisywać
nazw / opisów z migracji.

Użycie::

    .venv/bin/python manage.py seed_demo_data
    .venv/bin/python manage.py seed_demo_data --reset   # usuń demo i posiej od nowa
"""
from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction

from pages.models import StaticPage


STATIC_PAGES = [
    {
        "slug": "demo-o-wydziale",
        "title": "O Wydziale Sędziowskim (demo)",
        "body": (
            "<p>To jest przykładowa strona statyczna dodana przez "
            "<code>seed_demo_data</code>. Możesz ją swobodnie edytować "
            "w panelu admina — służy do klikania po layoucie.</p>"
            "<p>Prefiks slugu <code>demo-</code> ułatwia szybkie odsianie "
            "wpisów testowych od produkcyjnych.</p>"
        ),
    },
    {
        "slug": "demo-kontakt",
        "title": "Kontakt (demo)",
        "body": (
            "<p>E-mail: <a href=\"mailto:kontakt@example.local\">"
            "kontakt@example.local</a></p>"
            "<p>Ten wpis istnieje tylko lokalnie, żeby dało się sprawdzić "
            "render szablonu <code>pages/static_page.html</code>.</p>"
        ),
    },
    {
        "slug": "demo-regulamin",
        "title": "Regulamin (demo)",
        "body": (
            "<h2>§1. Postanowienia ogólne</h2>"
            "<p>Lorem ipsum dolor sit amet — dłuższy tekst przydaje się do "
            "sprawdzenia typografii i szerokości kolumn.</p>"
            "<h2>§2. Zakres</h2>"
            "<ol>"
            "<li>Pierwszy punkt regulaminu.</li>"
            "<li>Drugi punkt — dla kontroli list.</li>"
            "<li>Trzeci punkt — żeby padło na nieparzystą.</li>"
            "</ol>"
        ),
    },
]


class Command(BaseCommand):
    help = "Dodaje przykładowe strony statyczne (lokalne demo)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Najpierw usuń wpisy demo (slug rozpoczynający się od 'demo-').",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["reset"]:
            removed_pages = StaticPage.objects.filter(slug__startswith="demo-").delete()
            self.stdout.write(f"    reset: strony={removed_pages[0]}")

        created_pages = 0
        updated_pages = 0
        for data in STATIC_PAGES:
            _, created = StaticPage.objects.update_or_create(
                slug=data["slug"],
                defaults={
                    "title": data["title"],
                    "body": data["body"],
                    "is_published": True,
                },
            )
            if created:
                created_pages += 1
            else:
                updated_pages += 1

        self.stdout.write(self.style.SUCCESS(
            f"    strony statyczne: {created_pages} nowych, {updated_pages} zaktualizowanych"
        ))
        self.stdout.write(
            "    ➜ zajrzyj do panelu: /admin/pages/staticpage/"
        )
