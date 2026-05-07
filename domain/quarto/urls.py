from django.urls import path
from domain.quarto import views

app_name = "quarto"

urlpatterns = [
    path("listar-quartos/", views.listar_quartos_view, name="listar_quartos"),
    path("<int:pk>/", views.detalhe_quarto_view, name="detalhe_quarto"),
]