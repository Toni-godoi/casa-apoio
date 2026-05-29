from django.contrib import admin
from domain.pessoa.models import Pessoa, PessoaEditada

# Register your models here.
admin.site.register(Pessoa)
admin.site.register(PessoaEditada)