from django.conf import settings
from pathlib import Path


def site_settings(request):
    logo_path = Path(settings.BASE_DIR) / "static" / "images" / "logo.png"
    return {
        "STAFFING_SYSTEM_URL": getattr(settings, "STAFFING_SYSTEM_URL", "#"),
        "logo_exists": logo_path.exists(),
    }
