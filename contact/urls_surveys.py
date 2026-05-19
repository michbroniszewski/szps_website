from django.urls import path
from . import views

app_name = "surveys"

urlpatterns = [
    path("", views.surveys_list, name="list"),
    path("<int:pk>/", views.survey_detail, name="detail"),
    path("dziekujemy/", views.survey_done, name="done"),
]
