from django.urls import path

from . import views

app_name = "pages"

urlpatterns = [
    path("", views.home, name="home"),
    path("aktualnosci/", views.article_list, name="article_list"),
    path("aktualnosci/<slug:slug>/", views.article_detail, name="article_detail"),
    path("kontakt/wyslij/", views.contact_submit, name="contact_submit"),
    path("s/<slug:slug>/", views.static_page, name="static_page"),
]
