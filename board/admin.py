from django.contrib import admin

from .models import BoardMember


@admin.register(BoardMember)
class BoardMemberAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "role", "order", "is_active")
    list_editable = ("order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("first_name", "last_name", "role", "email")
    ordering = ("order", "last_name")
