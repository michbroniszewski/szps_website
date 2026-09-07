from django.urls import path

from . import views

app_name = "pages"

urlpatterns = [
    path("", views.home, name="home"),
    # Galeria tymczasowo wyłączona — czeka na model GalleryPhoto.
    # path("galeria/", views.gallery, name="gallery"),
    path("aktualnosci/<slug:slug>/", views.article_detail, name="article_detail"),
    path("s/<slug:slug>/", views.static_page, name="static_page"),
]
