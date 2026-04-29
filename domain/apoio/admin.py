from django.contrib import admin
from domain.apoio.models import Apoio, Acompanhante, Hospedagem, AlocacaoQuarto

# Register your models here.
admin.site.register(Apoio)
admin.site.register(Acompanhante)
admin.site.register(Hospedagem)
admin.site.register(AlocacaoQuarto)