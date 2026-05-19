from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from .sitemaps import StaticViewSitemap, NewsPostSitemap

sitemaps = {
    "static": StaticViewSitemap,
    "news": NewsPostSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("ckeditor5/", include("django_ckeditor_5.urls")),
    path("aktualnosci/", include("news.urls", namespace="news")),
    path("dokumenty/", include("documents.urls", namespace="documents")),
    path("sponsorzy/", include("sponsors.urls", namespace="sponsors")),
    path("kontakt/", include("contact.urls", namespace="contact")),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path("", include("news.urls_home")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
