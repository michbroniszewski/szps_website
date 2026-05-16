from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("ckeditor5/", include("django_ckeditor_5.urls")),
    path("aktualnosci/", include("news.urls", namespace="news")),
    path("dokumenty/", include("documents.urls", namespace="documents")),
    path("sponsorzy/", include("sponsors.urls", namespace="sponsors")),
    path("kontakt/", include("contact.urls", namespace="contact")),
    path("", include("news.urls_home")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
