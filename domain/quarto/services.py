from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import date, time, datetime
from typing import Optional
from domain.quarto.models import Quarto

@transaction.atomic
def cadastrar_quarto(
        *,
        identificacao:str,
        quantidadeVagas:int,
)->Quarto:
    
    _valida_quarto(identificacao)
    cadastro = timezone.localdate()

    quarto = Quarto(
        identificacao=identificacao,
        quantidadeVagas=quantidadeVagas,
        dataCadastro_quarto=cadastro
    )
    quarto.save()
    return quarto

@transaction.atomic
def editar_quarto(
        *,
        ed_quarto_id:int,
        ed_identificacao:str,
        ed_quantidadeVagas:int
):
    
    quarto = _existe_quarto(ed_quarto_id)
    if quarto:
        _valida_quarto_ativo(ed_quarto_id, "editado")

    campos_alterados = []
    if quarto.identificacao != ed_identificacao:
        campos_alterados.append("Descrição")
        quarto.identificacao = ed_identificacao
    if quarto.quantidadeVagas != ed_quantidadeVagas:
        campos_alterados.append("Quantidade vagas")
        quarto.quantidadeVagas = ed_quantidadeVagas
    
    quarto.save()
    return quarto

def desativar_quarto(
        *,
        ed_quarto_id:int
):
    quarto = _existe_quarto(ed_quarto_id)
    if quarto:
        _valida_quarto_ativo(ed_quarto_id, "desativado")
    
    quarto.status = False
    quarto.save()
    return quarto

def _valida_quarto_ativo(quarto_id:int, acao:str)->None:
    
    existe = Quarto.objects.filter(
        pk=quarto_id,
        status = True
    )
    if not existe:
        raise ValidationError(f"Quarto não encontrado ou desativado. Não pode ser {acao}")


def _existe_quarto(quarto_id:int)->Quarto:
    try:
        return Quarto.objects.get(pk=quarto_id)
    except Quarto.DoesNotExist:
        raise ValidationError("Quarto não encontrado")

def _valida_quarto(desc=str)->None:
    quarto_existe = Quarto.objects.filter(
        identificacao = desc,
        status = True
    )
    if quarto_existe.exists():
        raise ValidationError("Ja existe quarto com esta descrição")