from django.contrib import admin

from .models import Article, StaticPage


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "published_at", "is_published", "updated_at")
    list_filter = ("is_published", "published_at")
    search_fields = ("title", "lead", "body")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_at"
    ordering = ("-published_at",)


@admin.register(StaticPage)
class StaticPageAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_published", "updated_at")
    list_filter = ("is_published",)
    search_fields = ("title", "body")
    prepopulated_fields = {"slug": ("title",)}
