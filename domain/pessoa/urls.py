from django.urls import path
from domain.pessoa import views

app_name = "pessoa"

urlpatterns = [
    path("cadastrar-pessoa/", views.cadastrar_pessoa_view, name="cadastrar_pessoa"),
    path("<int:pk>/", views.dados_pessoa_view, name="dados_pessoa"),
    path("<int:pk>/editar/", views.editar_pessoa_view, name="editar_pessoa"),
    path("pessoas/", views.listar_pessoas_views, name="listar_pessoas"),
]