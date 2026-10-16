from urllib.parse import urlsplit

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


def is_safe_href(url: str) -> bool:
    """Ścieżka na tej stronie („/static/…”) albo adres http(s).

    Blokuje m.in. „javascript:…” i „data:…” — taki link na stronie głównej
    uruchomiłby kod w przeglądarce odwiedzającego. „//host” to adres
    zewnętrzny bez schematu, więc też odpada.
    """
    url = url.strip()
    if url.startswith("/") and not url.startswith("//"):
        return True
    parts = urlsplit(url)
    return parts.scheme in {"http", "https"} and bool(parts.netloc)


class DocumentCategory(models.Model):
    """Kategoria dokumentu — np. Komunikaty WS, Przepisy gry, Wytyczne."""

    name = models.CharField("Nazwa", max_length=100, unique=True)
    slug = models.SlugField("Slug", max_length=120, unique=True)
    description = models.CharField("Opis", max_length=250, blank=True)
    order = models.PositiveSmallIntegerField("Kolejność", default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Kategoria dokumentu"
        verbose_name_plural = "Kategorie dokumentów"

    def __str__(self) -> str:
        return self.name


class Document(models.Model):
    """Pojedynczy dokument — PDF, DOCX, obrazek itp."""

    title = models.CharField("Tytuł", max_length=200)
    category = models.ForeignKey(
        DocumentCategory,
        verbose_name="Kategoria",
        on_delete=models.PROTECT,
        related_name="documents",
    )
    file = models.FileField(
        "Plik",
        upload_to="documents/%Y/",
        blank=True,
        help_text="Prześlij plik z dysku ALBO podaj adres w polu poniżej.",
    )
    external_url = models.CharField(
        "Adres pliku",
        max_length=500,
        blank=True,
        help_text="Alternatywa dla pliku — np. „/static/dokumenty/x.pdf” "
        "albo pełny adres URL do dokumentu w innym miejscu.",
    )
    description = models.TextField("Opis", blank=True)
    published_at = models.DateField("Data publikacji", default=timezone.now)
    is_published = models.BooleanField("Widoczny na stronie", default=True)
    is_featured = models.BooleanField(
        "Wyróżniony",
        default=False,
        help_text="Pokazywany na górze sekcji Dokumenty jako baner "
        "(zamiast na liście w swojej kategorii).",
    )
    button_label = models.CharField(
        "Tekst przycisku",
        max_length=40,
        blank=True,
        help_text="Tylko dla wyróżnionych, np. „Pobierz PDF”. Puste = „Otwórz dokument”.",
    )

    class Meta:
        ordering = ["-published_at", "-id"]
        verbose_name = "Dokument"
        verbose_name_plural = "Dokumenty"

    def __str__(self) -> str:
        return self.title

    def clean(self):
        if not self.file and not self.external_url:
            raise ValidationError(
                "Podaj plik do przesłania ALBO adres w polu „Adres pliku”."
            )
        if self.external_url and not is_safe_href(self.external_url):
            raise ValidationError({
                "external_url": "Podaj ścieżkę zaczynającą się od „/” "
                "(np. /static/dokumenty/plik.pdf) albo pełny adres http(s)://."
            })

    def get_href(self) -> str:
        """Adres do linkowania z frontu — plik, jeśli jest; inaczej external_url."""
        if self.file:
            return self.file.url
        # Wpisy sprzed walidacji też nie mogą wstawić niebezpiecznego linku.
        return self.external_url.strip() if is_safe_href(self.external_url) else ""
