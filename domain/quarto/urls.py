from django.urls import path
from domain.quarto import views

app_name = "quarto"

urlpatterns = [
    path("cadastrar-quarto/", views.cadastrar_quarto_view, name="cadastrar_quarto"),
    #path("<int:pk>/editar-quarto/", views.editar_quarto_view, name="editar_quarto"),
    path("quartos-ativos/", views.listar_quartos_ativos_view, name="quartos_ativos"),
    path("quartos-desativados/", views.listar_quartos_desativados_view, name="quartos_desativados"),
    path("<int:pk>/", views.detalhe_quarto_view, name="detalhe_quarto"),
    path("<int:pk>/desativar", views.desativar_quarto_view, name="desativar_quarto"),
    path("designer/", views.designer, name="designer"),
]