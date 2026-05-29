from typing import Optional
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import date, time, datetime, timedelta
from domain.pessoa.models import Pessoa, PessoaEditada
from domain.solicitacao.models import FuncaoSolicitantePessoa, SolicitantePessoa

@transaction.atomic
def cadastrar_funcao_pessoa(
    *,
    funcao:str,
    descricao:Optional[str]=None
)->FuncaoSolicitantePessoa:
    
    funcao_solicitacao = FuncaoSolicitantePessoa(
        funcao = funcao,
        descricao = descricao
    )
    funcao_solicitacao.save()
    return funcao_solicitacao
@transaction.atomic

def excluir_funcao_pessoa(funcao_id):
    try:
        funcao = FuncaoSolicitantePessoa.objects.get(
            pk = funcao_id
        )
    except FuncaoSolicitantePessoa.DoesNotExist:
        raise ValidationError("Função não encontrada")

    if SolicitantePessoa.objects.filter(
        funcao=funcao
    ).exists():
        raise ValidationError("Essa função esta vinculada com solicitantes e não pode ser excluída")
    
    funcao.delete()

@transaction.atomic
def editar_funcao_pessoa(
        *,
        ed_funcao_id:int,
        ed_funcao:str,
        ed_descricao:Optional[str]=None
):
    
    funcao = _validar_funcao(ed_funcao_id)

    campos_alterados = []
    if funcao.funcao != ed_funcao:
        campos_alterados.append("Nome")
        funcao.funcao = ed_funcao
    if funcao.descricao != ed_descricao:
        campos_alterados.append("Descrição")
        funcao.descricao = ed_descricao
    funcao.save()
    return funcao
    
@transaction.atomic
def cadastrar_solicitante_pessoa(
    *,
    pessoa_id:int,
    funcao_id:int,
    descricao:Optional[str]=None
)->SolicitantePessoa:
    
    _valida_ja_solicitante(pessoa_id)
    
    pessoa = _validar_pessoa(pessoa_id)
    funcao = _validar_funcao(funcao_id)
    
    solicitante = SolicitantePessoa(
        pessoa = pessoa,
        funcao = funcao,
        descricao = descricao
    )
    solicitante.save()
    return solicitante

def editar_solicitante_pessoa(
        *,
        ed_solicitante_id:int,
        ed_pessoa_id:int,
        ed_funcao_id:int,
        ed_descricao:Optional[str]=None
):
    solicitante_pessoa = _validar_solicitante(ed_solicitante_id)
    pessoa = _validar_pessoa(ed_pessoa_id)
    funcao = _validar_funcao(ed_funcao_id)

    campos_alterados = []
    if solicitante_pessoa.pessoa != pessoa:
        campos_alterados.append("Pessoa")
        solicitante_pessoa.pessoa =pessoa
    if solicitante_pessoa.funcao != funcao:
        campos_alterados.append("Função")
        solicitante_pessoa.funcao = funcao
    if solicitante_pessoa.descricao != ed_descricao:
        campos_alterados.append("Função")
        solicitante_pessoa.descricao = ed_descricao

    solicitante_pessoa.save()
    return solicitante_pessoa

###
#Validações
###
def _valida_ja_solicitante(pessoa_id:int)->None:

    existe = SolicitantePessoa.objects.filter(
        pessoa = pessoa_id
    ).exists()
    if existe:
        raise ValidationError("Solicitante ja cadastrado")

def _validar_solicitante(solicitante_id)->SolicitantePessoa:
    try:
        return SolicitantePessoa.objects.get(pk=solicitante_id)
    except SolicitantePessoa.DoesNotExist:
        raise ValidationError("Solicitante não encontrado")
    
def _validar_funcao(funcao_id:int)->FuncaoSolicitantePessoa:
    try:
        return FuncaoSolicitantePessoa.objects.get(pk=funcao_id)
    except FuncaoSolicitantePessoa.DoesNotExist:
        raise ValidationError("Funcão de solicitante não encontrada")

def _validar_pessoa(pessoa_id=int)->Pessoa:
    try:
        return Pessoa.objects.get(pk=pessoa_id)
    except Pessoa.DoesNotExist:
        raise ValidationError("Pessoa para solicitante não encontrada")
