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
    list_display = ("title", "category", "published_at", "is_published", "is_featured")
    list_editable = ("is_featured",)
    list_filter = ("category", "is_published", "is_featured", "published_at")
    search_fields = ("title", "description")
    date_hierarchy = "published_at"
    fields = (
        "title",
        "category",
        "file",
        "external_url",
        "description",
        "published_at",
        "is_published",
        "is_featured",
        "button_label",
    )
