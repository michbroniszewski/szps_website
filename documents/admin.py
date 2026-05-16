from django.contrib import admin
from .models import Document, DocumentCategory


@admin.register(DocumentCategory)
class DocumentCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "order"]
    prepopulated_fields = {"slug": ("name",)}
    ordering = ["order"]


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "extension", "uploaded_at", "is_active"]
    list_filter = ["is_active", "category"]
    search_fields = ["title", "description"]
    list_editable = ["is_active"]
    date_hierarchy = "uploaded_at"
