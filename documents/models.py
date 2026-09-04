from django.db import models


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
    file = models.FileField("Plik", upload_to="documents/%Y/")
    description = models.TextField("Opis", blank=True)
    published_at = models.DateField("Data publikacji", auto_now_add=True)
    is_published = models.BooleanField("Widoczny na stronie", default=True)

    class Meta:
        ordering = ["-published_at", "-id"]
        verbose_name = "Dokument"
        verbose_name_plural = "Dokumenty"

    def __str__(self) -> str:
        return self.title
