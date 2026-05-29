from django.db import models
from domain.pessoa.models import Pessoa

# Create your models here.
class FuncaoSolicitantePessoa(models.Model):
    funcao = models.CharField(max_length=20, unique=True)
    descricao = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.funcao

class SolicitantePessoa(models.Model):
    pessoa = models.OneToOneField(Pessoa, on_delete=models.PROTECT)
    funcao = models.OneToOneField(FuncaoSolicitantePessoa, on_delete=models.PROTECT)
    descricao = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.pessoa} | {self.funcao}"