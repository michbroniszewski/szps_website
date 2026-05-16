from django.contrib import admin
from django.utils.html import format_html
from .models import NewsPost, NewsCategory


@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(NewsPost)
class NewsPostAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "is_published", "is_pinned", "published_at"]
    list_filter = ["is_published", "is_pinned", "category"]
    search_fields = ["title", "summary", "content"]
    prepopulated_fields = {"slug": ("title",)}
    list_editable = ["is_published", "is_pinned"]
    date_hierarchy = "published_at"
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = [
        ("Treść", {"fields": ["title", "slug", "category", "summary", "content", "image"]}),
        ("Publikacja", {"fields": ["is_published", "is_pinned", "published_at"]}),
        ("Metadane", {"fields": ["created_at", "updated_at"], "classes": ["collapse"]}),
    ]
