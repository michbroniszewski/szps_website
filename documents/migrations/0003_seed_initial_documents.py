"""Seed początkowy zbiór dokumentów, który wcześniej był zaszyty w
templates/pages/home.html. Wszystkie pozycje pokazują istniejące pliki
ze `static/dokumenty/` przez `external_url` — bez przenoszenia plików,
bez ruszania pipeline'u whitenoise.

Idempotentny — używa update_or_create po (title, category). Bezpieczny
też przy dostawianiu nowych dokumentów z admina: dokumenty utworzone
ręcznie nie zostaną nadpisane, jeśli mają inne tytuły.
"""

from datetime import date

from django.db import migrations


CATEGORIES = [
    {"name": "Przepisy gry", "slug": "przepisy-gry", "order": 10,
     "description": "Aktualne przepisy gry — wersja polska i FIVB."},
    {"name": "Wytyczne i instrukcje", "slug": "wytyczne-i-instrukcje", "order": 20,
     "description": "Interpretacje przepisów i wskazówki praktyczne."},
    {"name": "Materiały szkoleniowe", "slug": "materialy-szkoleniowe", "order": 30,
     "description": "Prezentacje, opracowania, materiały egzaminacyjne."},
    {"name": "Komunikaty", "slug": "komunikaty", "order": 40,
     "description": "Bieżące komunikaty Wydziału Sędziowskiego."},
]

DOCUMENTS = [
    # Przepisy gry (kolejność wstawiania = kolejność wyświetlania,
    # bo Meta.ordering to (-published_at, -id) — nowszy id wyżej).
    {"category_slug": "przepisy-gry",
     "title": "Official Volleyball Rules 2025–2028",
     "external_url": "/static/dokumenty/official-volleyball-rules-2025-2028.pdf",
     "description": "Oficjalne przepisy FIVB · PDF",
     "published_at": date(2025, 1, 1)},
    {"category_slug": "przepisy-gry",
     "title": "Przepisy gry 2025–2028",
     "external_url": "/static/dokumenty/przepisy-gry-2025-2028.pdf",
     "description": "Polska wersja przepisów · PDF",
     "published_at": date(2025, 1, 1)},
    # Wytyczne i instrukcje
    {"category_slug": "wytyczne-i-instrukcje",
     "title": "Wytyczne i instrukcje sędziowania 2025",
     "external_url": "/static/dokumenty/wytyczne-i-instrukcje-sedziowania-2025.pdf",
     "description": "Interpretacje przepisów i wskazówki praktyczne · PDF",
     "published_at": date(2025, 1, 1)},
    # Materiały szkoleniowe
    {"category_slug": "materialy-szkoleniowe",
     "title": "Mały protokół — prezentacja",
     "external_url": "/static/dokumenty/prezentacja-maly-protokol.pdf",
     "description": "Szkolenie z prowadzenia małego protokołu · PDF",
     "published_at": date(2025, 1, 1)},
    # Komunikaty (data w tytule → data w polu published_at)
    {"category_slug": "komunikaty",
     "title": "Komunikat WS — 27.05.2026",
     "external_url": "/static/dokumenty/Komunikat_WS_270526.pdf",
     "description": "Komunikat Wydziału Sędziowskiego · PDF",
     "published_at": date(2026, 5, 27)},
    {"category_slug": "komunikaty",
     "title": "Komunikat WS — 27.01.2026",
     "external_url": "/static/dokumenty/komunikat-ws-2026-01-27.pdf",
     "description": "Komunikat Wydziału Sędziowskiego · PDF",
     "published_at": date(2026, 1, 27)},
    {"category_slug": "komunikaty",
     "title": "Komunikat WS — 24.06.2025",
     "external_url": "/static/dokumenty/komunikat-ws-2025-06-24.pdf",
     "description": "Komunikat Wydziału Sędziowskiego · PDF",
     "published_at": date(2025, 6, 24)},
    {"category_slug": "komunikaty",
     "title": "Komunikat WS — 29.04.2025",
     "external_url": "/static/dokumenty/komunikat-ws-2025-04-29.pdf",
     "description": "Komunikat Wydziału Sędziowskiego · PDF",
     "published_at": date(2025, 4, 29)},
]


def seed_documents(apps, schema_editor):
    DocumentCategory = apps.get_model("documents", "DocumentCategory")
    Document = apps.get_model("documents", "Document")

    cats_by_slug = {}
    for cat_data in CATEGORIES:
        cat, _ = DocumentCategory.objects.update_or_create(
            slug=cat_data["slug"],
            defaults={
                "name": cat_data["name"],
                "order": cat_data["order"],
                "description": cat_data["description"],
            },
        )
        cats_by_slug[cat.slug] = cat

    for doc in DOCUMENTS:
        cat = cats_by_slug[doc["category_slug"]]
        Document.objects.update_or_create(
            category=cat,
            title=doc["title"],
            defaults={
                "external_url": doc["external_url"],
                "description": doc["description"],
                "published_at": doc["published_at"],
                "is_published": True,
            },
        )


def unseed_documents(apps, schema_editor):
    # Backwards migration usuwa tylko dokumenty, które zasialismy tu z tytułu.
    # Kategorie zostają — jeśli redakcja dołożyła do nich własne dokumenty,
    # nie chcemy ich stracić.
    Document = apps.get_model("documents", "Document")
    for doc in DOCUMENTS:
        Document.objects.filter(title=doc["title"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("documents", "0002_document_external_url_alter_document_file_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_documents, unseed_documents),
    ]
