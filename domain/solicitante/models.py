from django.db import models
from datetime import date
from django.utils import timezone
from domain.endereco.models import Endereco

# Create your models here.
class  UnidadeSolicitante(models.Model):
    nome_unidade = models.CharField(max_length=50)
    endereco = models.ForeignKey(Endereco, on_delete=models.PROTECT, related_name='endereco_unidade')

    def __str__(self):
        return self.nome_unidade
    
class SetorUnidadeSolicitante(models.Model):
    nome_setor = models.CharField(max_length=50)
    unidade_solicitante = models.ForeignKey(UnidadeSolicitante, on_delete=models.PROTECT, related_name='unidade_setor')

    def __str__(self):
        return f"{self.unidade_solicitante} | {self.nome_setor}"