from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

# Create your models here.
class Quarto(models.Model):
    #casaDeApoio
    identificacao = models.CharField(max_length=20)
    quantidadeVagas = models.IntegerField()
    vagasLivres = models.IntegerField(blank=True)
    dataCadastro_quarto = models.DateField()
    descricao = models.CharField(max_length=200, blank=True, null=True)
    status = models.BooleanField(default=True, verbose_name="Quarto ativo")

    def clean(self):
        if self.quantidadeVagas:
            if self.vagasLivres is None:
                self.vagasLivres = self.quantidadeVagas

        if self.vagasLivres > self.quantidadeVagas:
            raise ValidationError("Erro: vagas livres maior que  quantidade de vagas do quarto")
        
        quarto_existe = Quarto.objects.filter(
            identificacao = self.identificacao,
            status = True
        ).exclude(pk=self.pk)
        if quarto_existe.exists():
            raise ValidationError("Um quarto com essa descrição ja esta cadastrado")

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
        