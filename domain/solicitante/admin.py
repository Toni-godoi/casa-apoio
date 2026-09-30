from django.contrib import admin
from domain.solicitante.models import UnidadeSolicitante, SetorUnidadeSolicitante

# Register your models here.
admin.site.register(UnidadeSolicitante)
admin.site.register(SetorUnidadeSolicitante)