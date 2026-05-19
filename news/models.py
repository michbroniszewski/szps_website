from django.db import models
from django.urls import reverse
from django.utils import timezone
from django_ckeditor_5.fields import CKEditor5Field


class NewsCategory(models.Model):
    name = models.CharField("Nazwa kategorii", max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = "Kategoria"
        verbose_name_plural = "Kategorie"
        ordering = ["name"]

    def __str__(self):
        return self.name


class NewsPost(models.Model):
    title = models.CharField("Tytuł", max_length=300)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(
        NewsCategory, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="Kategoria", related_name="posts"
    )
    summary = models.TextField("Skrót", max_length=500, blank=True)
    content = CKEditor5Field("Treść", config_name="extends")
    image = models.ImageField("Zdjęcie", upload_to="news/images/", blank=True, null=True)
    published_at = models.DateTimeField("Data publikacji", default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField("Opublikowany", default=False)
    is_pinned = models.BooleanField("Przypięty", default=False)

    class Meta:
        verbose_name = "Aktualność"
        verbose_name_plural = "Aktualności"
        ordering = ["-is_pinned", "-published_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("news:detail", kwargs={"slug": self.slug})
