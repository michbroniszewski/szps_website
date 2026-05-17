from django.contrib import admin
from .models import Document, DocumentCategory


@admin.register(DocumentCategory)
class DocumentCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "order"]
    prepopulated_fields = {"slug": ("name",)}
    ordering = ["order"]


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "extension", "uploaded_at", "is_active", "is_featured"]
    list_filter = ["is_active", "is_featured", "category"]
    search_fields = ["title", "description"]
    list_editable = ["is_active", "is_featured"]
    date_hierarchy = "uploaded_at"
