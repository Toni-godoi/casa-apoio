from django.utils import timezone

def calcular_idade(data_nascimento):
    hoje = timezone.localdate()
    idade = (hoje.year - data_nascimento.year - ((hoje.month, hoje.day)<(data_nascimento.month,data_nascimento.day)))
    return idade