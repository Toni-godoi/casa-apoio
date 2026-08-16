from django.urls import path
from domain.endereco import views

app_name = "endereco"

urlpatterns = [
    path("cidades/", views.listar_estados, name="listar_enderecos"),
    path("cidades/cadastrar-cidade", views.w_cadastrar_cidade, name="cadastrar_cidade"),
    path("cidade/<int:pk>/bairros", views.listar_bairros, name="listar_bairros"),
    path("cidade/<int:pk>/bairros/novo", views.w_cadastrar_bairro, name="novo_bairro"),
    path("cidade/<int:pk>/bairro/<int:pk_bairro>/editar>", views.w_editar_bairro, name="editar_bairro"),
]