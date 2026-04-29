from datetime import date
from django.utils import timezone
from django.db import models
from django.forms import ValidationError

# Create your models here.
class PapelSolicitante(models.Model):
    nome = models.CharField(max_length=50)

    def __str__(self):
        return self.nome
    
class Pessoa(models.Model):
    nome_pessoa = models.CharField(max_length=30)
    cpf_pessoa = models.CharField(max_length=11, unique=True)
    dataNasc_pessoa = models.DateField()
    telefone_pessoa = models.CharField(max_length=11)
    email_pessoa = models.EmailField(max_length=80, unique=True)
    aptaSolicitante_pessoa = models.BooleanField(default=False)
    papelSolicitante_pessoa = models.ForeignKey(PapelSolicitante, null=True, blank=True, on_delete=models.PROTECT)
    dataCadastro = models.DateField(auto_now_add=True)

    def clean(self):
        if self.aptaSolicitante_pessoa == True and not self.papelSolicitante_pessoa:
            raise ValidationError("precisa informar função da pessoa")
        
    def __str__(self):
        return self.nome_pessoa
    
    def eh_menor_idade(self):
        hoje = date.today()
        idade = hoje.year - self.dataNasc_pessoa.year

        if (hoje.month, hoje.day) < (self.dataNasc_pessoa.month, self.dataNasc_pessoa.day):
            idade -= 1
        return idade < 18

#class DocumentoFoto(models.Model)