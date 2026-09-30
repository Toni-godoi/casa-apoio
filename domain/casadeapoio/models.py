from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from domain.endereco.models import Endereco
# Create your models here.

class CasaDeApoio(models.Model):
    nome_casaApoio = models.CharField(max_length=200, unique=True, blank=False)
    endereco = models.ForeignKey(Endereco, on_delete=models.PROTECT, blank=True, null=True)

    def __str__(self):
        return self.nome_casaApoio