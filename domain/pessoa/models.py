from datetime import date
from django.utils import timezone
from django.db import models
from django.forms import ValidationError
from domain.endereco.models import Endereco

# Create your models here.
class Pessoa(models.Model):
    SEXO_CHOICES = [('M', 'Masculino'), ('F', 'Feminino')]
    PAIS_CHOICES = [('BR','Brasil'), ('PY', 'Paraguai')]
    nome_pessoa = models.CharField(max_length=30)
    cpf_pessoa = models.CharField(max_length=11, unique=True)
    sexo_pessoa = models.CharField(max_length=1, choices=SEXO_CHOICES)
    dataNasc_pessoa = models.DateField()
    nacionalidade_pessoa = models.CharField(max_length=20, choices=PAIS_CHOICES, default='BR')
    telefone_pessoa = models.CharField(max_length=11)
    email_pessoa = models.EmailField(max_length=80)
    dataCadastro = models.DateField()
    descricao_pessoa = models.CharField(max_length=50, blank=True)
    #endereco = models.ForeignKey(Endereco, on_delete=models.CASCADE)

    #def clean(self):
    #def save(self, *args, **kwargs):
       # self.full_clean()
        #super().save(*args, **kwargs)
    
    def eh_menor_idade(self):
        hoje = date.today()
        idade = hoje.year - self.dataNasc_pessoa.year

        if (hoje.month, hoje.day) < (self.dataNasc_pessoa.month, self.dataNasc_pessoa.day):
            idade -= 1
        return idade < 18
    
    @property
    def idade(self):
        hoje = timezone.localdate()
        idade = (
            hoje.year - self.dataNasc_pessoa.year - (
                (hoje.month, hoje.day) < (self.dataNasc_pessoa.month, self.dataNasc_pessoa.day)
            )
        )
        return idade
    
    def __str__(self):
        return self.nome_pessoa
    

#class DocumentoFoto(models.Model)

class PessoaEditada(models.Model):
    pessoa = models.ForeignKey(Pessoa, on_delete=models.CASCADE, null=False, related_name="edicao")
    dataEdicao = models.DateTimeField()
    camposAlterados = models.TextField()

    def __str__(self):
        return f"{self.pessoa.nome_pessoa} | {self.dataEdicao}"
