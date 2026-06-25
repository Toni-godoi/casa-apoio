from django.contrib import admin
from domain.apoio.models import Apoio, Acompanhante, Hospedagem, AlocacaoQuarto, HistoricoPacienteApoio

# Register your models here.
admin.site.register(Apoio)
admin.site.register(Acompanhante)
admin.site.register(Hospedagem)
admin.site.register(AlocacaoQuarto)
admin.site.register(HistoricoPacienteApoio)