from django.urls import path
from domain.solicitacao import views

app_name = "solicitacao"

urlpatterns = [
    path("cadastrar-funcao/", views.cadastrar_funcao_view, name="cadastrar_funcao"),
    path("listar-funcoes/", views.listar_funcoes_view, name="listar_funcoes"),
    path("<int:pk>/", views.dados_funcao_view, name="dados_funcao"),
    path("<int:pk>/editar-funcao/", views.editar_funcao_view, name="editar_funcao"),
    path("<int:pk>/excluir/", views.excluir_funcao_view, name="excluir_funcao"),
    path("cadastrar-solicitante/", views.cadastrar_solicitante_view, name="cadastrar_solicitante"),
    path("listar-solicitantes/", views.listar_solicitantes_view, name="listar_solicitantes"),
    path("<int:pk>/editar-solicitante/", views.editar_solicitante_view, name="editar_solicitante"),
]