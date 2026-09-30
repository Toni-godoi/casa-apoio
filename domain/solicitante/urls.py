from django.urls import path
from domain.solicitante import views

app_name = "solicitante"

urlpatterns = [
    path("origens/", views.listar_origens_view, name="listar_origens"),
]