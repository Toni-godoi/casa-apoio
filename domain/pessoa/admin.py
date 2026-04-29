from django.contrib import admin
from domain.pessoa.models import Pessoa, PapelSolicitante

# Register your models here.
admin.site.register(Pessoa)
admin.site.register(PapelSolicitante)