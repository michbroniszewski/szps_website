from django.conf import settings
from pathlib import Path


def site_settings(request):
    logo_url = _find_logo()
    site_url = getattr(settings, "SITE_URL", "").rstrip("/")
    return {
        "STAFFING_SYSTEM_URL": getattr(settings, "STAFFING_SYSTEM_URL", "#"),
        "logo_exists": bool(logo_url),
        "logo_url": logo_url,
        "SITE_URL": site_url,
        "CANONICAL_URL": site_url + request.path,
    }


def _find_logo():
    images_dir = Path(settings.BASE_DIR) / "static" / "images"
    for ext in ("png", "svg", "jpg", "jpeg", "webp"):
        for name in (f"logo.{ext}", f"szps.{ext}", f"herb.{ext}"):
            candidate = images_dir / name
            if candidate.exists():
                return f"/static/images/{name}"
    return None

