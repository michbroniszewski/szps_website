from django.contrib import admin
from django.db import models
from django.utils.html import format_html
from tinymce.widgets import TinyMCE
from unfold.admin import ModelAdmin

from .models import Article, StaticPage


@admin.register(Article)
class ArticleAdmin(ModelAdmin):
    list_display = (
        "cover_thumb",
        "title",
        "badge_label",
        "published_at",
        "is_published",
        "updated_at",
    )
    list_display_links = ("cover_thumb", "title")
    list_filter = ("is_published", "badge_color", "published_at")
    search_fields = ("title", "lead", "body", "body_extended")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_at"
    ordering = ("-published_at",)
    fieldsets = (
        (None, {"fields": ("title", "slug", "lead", "is_published", "published_at")}),
        ("Treść", {"fields": ("body", "body_extended", "cover")}),
        (
            "Etykieta i wygląd kafla",
            {"fields": ("badge_color", "badge_label", "glyph")},
        ),
    )
    formfield_overrides = {
        models.TextField: {"widget": TinyMCE()},
    }

    @admin.display(description="Okładka")
    def cover_thumb(self, obj):
        if obj.cover:
            return format_html(
                '<img src="{}" style="height:40px;width:auto;border-radius:4px;'
                'object-fit:cover" alt="">',
                obj.cover.url,
            )
        return "—"


@admin.register(StaticPage)
class StaticPageAdmin(ModelAdmin):
    list_display = ("title", "slug", "is_published", "updated_at")
    list_filter = ("is_published",)
    search_fields = ("title", "body")
    prepopulated_fields = {"slug": ("title",)}
    formfield_overrides = {
        models.TextField: {"widget": TinyMCE()},
    }
