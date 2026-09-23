from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin

from .models import BoardMember


@admin.register(BoardMember)
class BoardMemberAdmin(ModelAdmin):
    list_display = (
        "photo_thumb",
        "last_name",
        "first_name",
        "role",
        "order",
        "is_active",
    )
    list_display_links = ("photo_thumb", "last_name")
    list_editable = ("order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("first_name", "last_name", "role", "email")
    ordering = ("order", "last_name")

    @admin.display(description="Zdjęcie")
    def photo_thumb(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="height:40px;width:40px;border-radius:50%;'
                'object-fit:cover" alt="">',
                obj.photo.url,
            )
        return "—"
