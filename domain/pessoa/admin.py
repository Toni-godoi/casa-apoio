from django.contrib import admin
from domain.pessoa.models import Pessoa, PessoaEditada, FotoPerfilPessoa, Deficiencia, DeficienciaPessoa

# Register your models here.
admin.site.register(Pessoa)
admin.site.register(PessoaEditada)
admin.site.register(FotoPerfilPessoa)
admin.site.register(Deficiencia)
admin.site.register(DeficienciaPessoa)