from django.contrib import admin
from .models import Sponsor


@admin.register(Sponsor)
class SponsorAdmin(admin.ModelAdmin):
    list_display = ["name", "tier", "order", "is_active", "website_url"]
    list_filter = ["tier", "is_active"]
    list_editable = ["order", "is_active", "tier"]
    search_fields = ["name", "description"]
