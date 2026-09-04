from django.db import migrations
from django.utils.timezone import make_aware
from datetime import datetime


ARTICLES = [
    {
        "slug": "awans-piotr-polak-szczebel-centralny",
        "title": "Awans na szczebel centralny!",
        "lead": "",
        "body": (
            "<p>Piotr Polak z awansem na szczebel centralny! 👏 Gratulujemy "
            "naszemu koledze świetnego egzaminu i postawy na boisku.</p>"
        ),
        "body_extended": (
            "<p>Piotr wykazał się bardzo dobrą znajomością przepisów gry, "
            "wytycznych i księgi przypadków oraz znakomitą postawą podczas "
            "sędziowanych meczów, co zaowocowało pozytywną oceną Komisji "
            "Egzaminacyjnej.</p>"
            "<p>Nasz kolega sędziował również mecz o złoto turnieju męskiego "
            "w roli S2. Gratulacje! 👏</p>"
        ),
        "badge_color": "gold",
        "badge_label": "Awans",
        "glyph": "▲",
        "published_at": datetime(2026, 5, 24, 10, 0),
    },
    {
        "slug": "szkolenie-przedsezonowe-siatkowka-plazowa",
        "title": "Szkolenie przedsezonowe — siatkówka plażowa",
        "lead": "",
        "body": (
            "<p>Już niebawem rozpoczynamy sezon siatkówki plażowej 🏖️ Zanim "
            "ruszą rozgrywki, czeka nas szkolenie dla wszystkich, którzy chcą "
            "sędziować plażową odmianę siatkówki. 🏐</p>"
        ),
        "body_extended": (
            "<p>Trwają zgłoszenia na uprawnienia w sezonie 2026. Zgłoszenia "
            "prosimy przesyłać na adres "
            "<a href=\"mailto:r.blachucinski@gmail.com\">r.blachucinski@gmail.com</a>, "
            "wpisując w tytule: <em>„ZGŁOSZENIE – siatkówka plażowa”</em>.</p>"
            "<p>Sędziowie szczebla centralnego proszeni są o informację o "
            "swojej dyspozycyjności — jej brak będzie traktowany jako rezygnacja.</p>"
            "<ul class=\"news-card__schedule\">"
            "<li><b>📚 Szkolenie teoretyczne</b><span>06.05, godz. 18:00 — "
            "Będzin Arena <i>(obowiązkowe dla wszystkich)</i></span></li>"
            "<li><b>🏐 Szkolenie praktyczne</b><span>09.05 — boiska przy SP 44 "
            "w Katowicach <i>(dla nowych sędziów oraz sędziów z rocznym stażem)</i>"
            "</span></li>"
            "</ul>"
            "<p class=\"news-card__credit\">Do zobaczenia na piasku ☀️ &nbsp;📸 SportAdventure51</p>"
        ),
        "badge_color": "green",
        "badge_label": "Szkolenie",
        "glyph": "★",
        "published_at": datetime(2026, 4, 30, 10, 0),
    },
]


def seed_articles(apps, schema_editor):
    Article = apps.get_model("pages", "Article")
    for data in ARTICLES:
        Article.objects.update_or_create(
            slug=data["slug"],
            defaults={
                "title": data["title"],
                "lead": data["lead"],
                "body": data["body"],
                "body_extended": data["body_extended"],
                "badge_color": data["badge_color"],
                "badge_label": data["badge_label"],
                "glyph": data["glyph"],
                "published_at": make_aware(data["published_at"]),
                "is_published": True,
            },
        )


def unseed_articles(apps, schema_editor):
    Article = apps.get_model("pages", "Article")
    Article.objects.filter(slug__in=[a["slug"] for a in ARTICLES]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("pages", "0002_article_badge_color_article_badge_label_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_articles, unseed_articles),
    ]
