from django.conf import settings


def site_settings(request):
    return {
        "STAFFING_SYSTEM_URL": getattr(settings, "STAFFING_SYSTEM_URL", "#"),
    }
