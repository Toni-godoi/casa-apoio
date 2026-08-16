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
        descricao:Optional[str]=None,
)->Quarto:
    
    _valida_quarto(identificacao)
    cadastro = timezone.localdate()

    quarto = Quarto(
        identificacao=identificacao,
        descricao = descricao,
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
        ed_descricao:Optional[str]=None,
        ed_quantidadeVagas:int
):
    
    quarto = _existe_quarto(ed_quarto_id)
    if quarto:
        _valida_quarto_ativo(ed_quarto_id, "editado")

    campos_alterados = []
    if quarto.identificacao != ed_identificacao:
        raise ValidationError("Não é possivel alterar a identificação do quarto. Considere desativa-lo e criar um novo quarto")
    if quarto.quantidadeVagas != ed_quantidadeVagas:
        qtd_vagas, vagas_livres = _remanejo_vagas(quarto, ed_quantidadeVagas)
        campos_alterados.append("Quantidade vagas")
        quarto.quantidadeVagas = qtd_vagas
        quarto.vagasLivres = vagas_livres
    if quarto.descricao != ed_descricao:
        quarto.descricao = ed_descricao
    
    quarto.save()
    return quarto

def desativar_quarto(
        *,
        ed_quarto_id:int
):
    quarto = _existe_quarto(ed_quarto_id)
    if quarto:
        _valida_quarto_ativo(ed_quarto_id, "desativado")
        _valida_tem_hospedes(quarto)
    
    quarto.status = False
    quarto.save()
    return quarto

def _valida_tem_hospedes(quarto:Quarto)->None:
    if quarto.quarto_alocacao.filter(hospedagem__apoio__status = True).exists():
        raise ValidationError("Não é possivel desativar com hospedagem de apoios ativos")

def _valida_quarto_ativo(quarto_id:int, acao:str)->None:
    
    existe = Quarto.objects.filter(pk=quarto_id, status = True)
    if not existe:
        raise ValidationError(f"Quarto não encontrado ou desativado. Não pode ser {acao}")

def  _remanejo_vagas(quarto:Quarto, ed_qtdVagas:int) -> tuple[int, int]:
    
    vagas_usadas = quarto.quantidadeVagas - quarto.vagasLivres
    novas_vagas_livres = ed_qtdVagas - vagas_usadas

    if ed_qtdVagas < quarto.quantidadeVagas:
        if ed_qtdVagas < vagas_usadas:
            raise ValidationError("A quantidade de vagas deve ser igual ou maior a quantidade ocupada")
        else:
            return ed_qtdVagas, novas_vagas_livres
        
    if ed_qtdVagas > quarto.quantidadeVagas:
        return ed_qtdVagas, novas_vagas_livres
     
    
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