from django.db import models


class DocumentCategory(models.Model):
    name = models.CharField("Nazwa kategorii", max_length=150)
    slug = models.SlugField(unique=True)
    order = models.PositiveIntegerField("Kolejność", default=0)

    class Meta:
        verbose_name = "Kategoria dokumentów"
        verbose_name_plural = "Kategorie dokumentów"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class Document(models.Model):
    title = models.CharField("Tytuł", max_length=300)
    description = models.TextField("Opis", blank=True)
    file = models.FileField("Plik", upload_to="documents/")
    category = models.ForeignKey(
        DocumentCategory, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="Kategoria", related_name="documents"
    )
    uploaded_at = models.DateTimeField("Data dodania", auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField("Aktywny", default=True)
    is_featured = models.BooleanField("Wyróżniony (strona główna)", default=False)

    class Meta:
        verbose_name = "Dokument"
        verbose_name_plural = "Dokumenty"
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.title

    def extension(self):
        name = self.file.name
        return name.split(".")[-1].upper() if "." in name else "PLIK"
