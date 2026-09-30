from django.db import models

# Create your models here.
class Pais(models.Model):
    nome_pais = models.CharField(max_length=20, null=False, blank=False, unique=True)
    sigla_pais = models.CharField(max_length=2, null=False, blank=False, unique=True)
    def __str__(self):
            return self.nome_pais

class Estado(models.Model):
    pais = models.ForeignKey(Pais, on_delete=models.PROTECT, related_name='pais_estado')
    nome_estado = models.CharField(max_length=20, null=False, blank=False, unique=True)
    uf_estado = models.CharField(max_length=2, null=False, blank=False)

    def __str__(self):
        return self.nome_estado

class Cidade(models.Model):
    estado = models.ForeignKey(Estado, on_delete=models.PROTECT, related_name='estado_cidade')
    nome_cidade = models.CharField(max_length=100, null=False, blank=False)

    def __str__(self):
            return f"{self.nome_cidade}"

class Bairro(models.Model):
    cidade = models.ForeignKey(Cidade, on_delete=models.PROTECT, related_name='cidade_bairro')
    nome_bairro = models.CharField(max_length=100, null=False, blank=False)

    def __str__(self):
        return f"{self.nome_bairro}"

class Endereco(models.Model):
    cep = models.CharField(max_length=9)
    bairro = models.ForeignKey(Bairro, on_delete=models.PROTECT, related_name='bairro_endereco')
    logradouro = models.CharField(max_length=200, null=False, blank=False)
    numero = models.CharField(max_length=20)
    complemento = models.CharField(max_length=50, blank=True)
    descricao = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return (f"{self.logradouro}, {self.numero}")

