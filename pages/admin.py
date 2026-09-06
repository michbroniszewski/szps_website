from django.contrib import admin

from .models import Article, StaticPage


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "badge_label", "published_at", "is_published", "updated_at")
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


@admin.register(StaticPage)
class StaticPageAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_published", "updated_at")
    list_filter = ("is_published",)
    search_fields = ("title", "body")
    prepopulated_fields = {"slug": ("title",)}
