from django.contrib import admin
from domain.endereco.models import Endereco, Pais, Estado, Cidade, Bairro

# Register your models here.
admin.site.register(Endereco)
admin.site.register(Pais)
admin.site.register(Estado)
admin.site.register(Cidade)
admin.site.register(Bairro)