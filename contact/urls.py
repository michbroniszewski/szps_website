from django.urls import path
from . import views

app_name = "contact"

urlpatterns = [
    path("", views.contact, name="contact"),
    path("ankieta/<int:pk>/", views.survey_detail, name="survey"),
    path("ankieta/dziekujemy/", views.survey_done, name="survey_done"),
]
