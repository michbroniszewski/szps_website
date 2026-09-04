from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Panel administracyjny — Wydział Sędziowski ŚZPS"
admin.site.site_title = "Panel ŚZPS"
admin.site.index_title = "Zarządzanie treścią"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("pages.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
