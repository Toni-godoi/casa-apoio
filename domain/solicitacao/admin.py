from django.contrib import admin
from domain.solicitacao.models import SolicitantePessoa, FuncaoSolicitantePessoa

# Register your models here.
admin.site.register(SolicitantePessoa)
admin.site.register(FuncaoSolicitantePessoa)