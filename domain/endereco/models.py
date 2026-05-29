from django.db import models

# Create your models here.
class Endereco(models.Model):
    ESTADO_CHOICES = [
        ("AC", "Acre"),
        ("AL", "Alagoas"),
        ("AP", "Amapá"),
        ("AM", "Amazonas"),
        ("BA", "Bahia"),
        ("CE", "Ceará"),
        ("DF", "Distrito Federal"),
        ("ES", "Espírito Santo"),
        ("GO", "Goiás"),
        ("MA", "Maranhão"),
        ("MT", "Mato Grosso"),
        ("MS", "Mato Grosso do Sul"),
        ("MG", "Minas Gerais"),
        ("PA", "Pará"),
        ("PB", "Paraíba"),
        ("PR", "Paraná"),
        ("PE", "Pernambuco"),
        ("PI", "Piauí"),
        ("RJ", "Rio de Janeiro"),
        ("RN", "Rio Grande do Norte"),
        ("RS", "Rio Grande do Sul"),
        ("RO", "Rondônia"),
        ("RR", "Roraima"),
        ("SC", "Santa Catarina"),
        ("SP", "São Paulo"),
        ("SE", "Sergipe"),
        ("TO", "Tocantins"),
    ]
    cep = models.CharField(max_length=9)
    estado = models.CharField(max_length=2, choices=ESTADO_CHOICES, null=False, blank=False)
    cidade = models.CharField(max_length=100, null=False, blank=False)
    bairro = models.CharField(max_length=100, null=False, blank=False)
    logradouro = models.CharField(max_length=200, null=False, blank=False)
    numero = models.CharField(max_length=20)
    complemento = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.logradouro}, {self.numero}"