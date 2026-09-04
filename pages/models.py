from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class Article(models.Model):
    """Aktualność / wpis na stronie głównej."""

    class BadgeColor(models.TextChoices):
        GOLD = "gold", "Złoty (awans, sukces)"
        GREEN = "green", "Zielony (szkolenie)"
        BLUE = "blue", "Niebieski (informacja)"
        RED = "red", "Czerwony (ważne)"
        NONE = "", "Bez etykiety"

    title = models.CharField("Tytuł", max_length=200)
    slug = models.SlugField("Slug (adres URL)", max_length=220, unique=True, blank=True)
    lead = models.CharField("Zajawka", max_length=300, blank=True)
    body = models.TextField(
        "Treść (widoczna od razu)",
        help_text="Krótki wstęp widoczny bez klikania „Czytaj więcej”. HTML dozwolony.",
    )
    body_extended = models.TextField(
        "Treść rozwijana",
        blank=True,
        help_text="Dalsza część artykułu pod przyciskiem „Czytaj więcej”. HTML dozwolony.",
    )
    badge_color = models.CharField(
        "Kolor etykiety",
        max_length=10,
        choices=BadgeColor.choices,
        default=BadgeColor.NONE,
        blank=True,
    )
    badge_label = models.CharField(
        "Tekst etykiety",
        max_length=40,
        blank=True,
        help_text="np. „Awans”, „Szkolenie”. Puste = bez etykiety.",
    )
    glyph = models.CharField(
        "Symbol na kaflu",
        max_length=4,
        blank=True,
        help_text="Pojedynczy znak/emoji wyświetlany na tle kafla (np. ▲, ★, 🏐).",
    )
    cover = models.ImageField("Obrazek", upload_to="articles/", blank=True)
    published_at = models.DateTimeField("Data publikacji", default=timezone.now)
    is_published = models.BooleanField("Opublikowana", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_at"]
        verbose_name = "Aktualność"
        verbose_name_plural = "Aktualności"

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=False)[:220] or "aktualnosc"
        super().save(*args, **kwargs)


class StaticPage(models.Model):
    """Strona z treścią redagowaną (np. o wydziale, kontakt, regulamin)."""

    title = models.CharField("Tytuł", max_length=200)
    slug = models.SlugField("Slug (adres URL)", max_length=220, unique=True)
    body = models.TextField("Treść", help_text="Możesz używać HTML.")
    is_published = models.BooleanField("Opublikowana", default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]
        verbose_name = "Strona statyczna"
        verbose_name_plural = "Strony statyczne"

    def __str__(self) -> str:
        return self.title
