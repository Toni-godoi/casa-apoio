from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

# Create your models here.

class CasaDeApoio(models.Model):
    nome_casaApoio = models.CharField(max_length=200, unique=True, blank=False)

    def __str__(self):
        return self.nome_casaApoio

class Quarto(models.Model):
    numero_quarto = models.IntegerField(max_length=3, unique=True)
    bloco_quarto = models.CharField(max_length=2)
    andar_quarto = models.CharField(max_length=2)
    capacidadePacientes_quarto = models.IntegerField(max_length=2)
    sexo_quarto = 'masculino', 'femenino', 'unisex'
    descricao_quarto = models.CharField(max_length=50)

    def __str__(self):
        return self.numero_quarto