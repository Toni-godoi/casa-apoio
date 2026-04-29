from django.urls import path
from domain.apoio import views

app_name = "apoio"

urlpatterns = [
    path("iniciar-apoio/", views.iniciar_apoio_view, name="iniciar"),
    path("<int:pk>/", views.detalhe_apoio_view, name="detalhe"),
    path("<int:pk>/novo-acompanhante/", views.adicionar_acompanhante_view, name="adicionar_acompanhante"),
    path("<int:pk>/checkout-acompanhante/", views.checkout_acompanhante_view, name="checkout_acompanhante"),
    path("<int:pk>/checkin-paciente/", views.checkin_apoio_view, name="checkin_paciente"),
    path("<int:pk>/checkout-paciente/", views.checkout_apoio_view, name="checkout_paciente"),
]