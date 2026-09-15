from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Document, DocumentCategory


@admin.register(DocumentCategory)
class DocumentCategoryAdmin(ModelAdmin):
    list_display = ("name", "slug", "order")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("order", "name")


@admin.register(Document)
class DocumentAdmin(ModelAdmin):
    list_display = ("title", "category", "published_at", "is_published")
    list_filter = ("category", "is_published", "published_at")
    search_fields = ("title", "description")
    date_hierarchy = "published_at"
