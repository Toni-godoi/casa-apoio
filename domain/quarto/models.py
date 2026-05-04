from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

# Create your models here.
class Quarto(models.Model):
    #casaDeApoio
    identificacao = models.CharField(max_length=100, unique=True)
    quantidadeVagas = models.IntegerField()
    vagasLivres = models.IntegerField(blank=True)
    status = models.BooleanField(default=True, verbose_name="Quarto ativo")

    def clean(self):
        if self.quantidadeVagas:
            if self.vagasLivres is None:
                self.vagasLivres = self.quantidadeVagas

        if self.vagasLivres > self.quantidadeVagas:
            raise ValidationError("Erro: vagas livres maior que  quantidade de vagas do quarto")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.identificacao
    
    def preenche_vaga(self):
        if self.vagasLivres <= 0:
            raise ValidationError("sem vagas disponivel")
        
        self.vagasLivres -= 1
        self.save()
    
    def liberar_vaga(self):
        if self.vagasLivres >= self.quantidadeVagas:
            raise ValidationError("Erro: vagas livres maior que vagas qtd de vagas do quarto")
        
        self.vagasLivres += 1
        self.save()
    
    def verifica_vagasLivres(self):
        return self.vagasLivres
        