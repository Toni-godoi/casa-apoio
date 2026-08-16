import re
import requests
import urllib.error
import urllib.request
import json
from django.db import transaction
from dataclasses import dataclass
from django.core.exceptions import ValidationError
from typing import Optional
from domain.endereco.models import Endereco, Pais, Estado, Cidade, Bairro

@transaction.atomic
def cadastrar_bairro(
    *,
    cidade=int,
    bairro=str,
)->Bairro:

    cidade_valido = _valida_cidade(cidade)

    bairro = Bairro(
        cidade = cidade_valido,
        bairro = bairro
    )
    bairro.save()
    return bairro

@transaction.atomic
def editar_bairro(
    *,
    ed_bairro=str,
    bairro_id = int
)->Bairro:

    bairro_valido = _existe_bairro(bairro_id)

    if bairro_valido.bairro != ed_bairro:
        bairro_valido.bairro = ed_bairro

    bairro_valido.save()
    return bairro_valido

@transaction.atomic
def cadastrar_cidade(
    *,
    estado=int,
    cidade=str,
)->Cidade:

    estado_valido = _valida_estado(estado)

    cidade = Cidade(
        estado = estado_valido,
        cidade = cidade
    )
    cidade.save()
    return cidade


@transaction.atomic
def cadastrar_end_pessoa(
    *,
    pais:int,
    estado:int,
    cidade:int,
    bairro:int,
    cep:Optional[int]=None,
    logradouro:Optional[str]=None,
    numero:Optional[int]=None,
    complemento:Optional[str]=None,
    descricao:Optional[str]=None,
)->Endereco:

    brasil = Pais.objects.get(pais="Brasil")
    if not pais:
        raise ValidationError("Selecione pais")
    if pais == brasil.pk:
        if not estado:
            raise ValidationError("Selecione estado")
        if not cidade:
            raise ValidationError("Selecione cidade")
        if not bairro:
            raise ValidationError("Selecione o bairro")
        if not cep:
            raise ValidationError("informe o cep")
        if not logradouro:
            raise ValidationError("Informe o logradouro")
    
    bairro_valido = _existe_bairro(bairro)
    if bairro_valido:
        _valida_cidade_estado_pais(bairro_valido, cidade, estado, pais)

    endereco = Endereco(
        cep = cep,
        bairro = bairro_valido,
        logradouro = logradouro,
        numero = numero,
        complemento = complemento,
        descricao = descricao
    )
    endereco.save()
    return endereco

@transaction.atomic
def editar_end_pessoa(
    *,
    ed_endereco_id:int,
    ed_pais:int,
    ed_cep:Optional[int]=None,
    ed_estado:int,
    ed_cidade:int,
    ed_bairro:int,
    ed_logradouro:Optional[str]=None,
    ed_numero:Optional[int]=None,
    ed_complemento:Optional[str]=None,
    ed_descricao:Optional[str]=None,
    ):

    endereco = _existe_endereco(ed_endereco_id)

    if not ed_pais:
        raise ValidationError("Selecione pais")
    brasil = Pais.objects.get(pais="Brasil")
    
    if ed_pais == brasil.pk:
        if not ed_estado:
            raise ValidationError("Selecione estado")
        if not ed_cidade:
            raise ValidationError("Selecione cidade")
        if not ed_bairro:
            raise ValidationError("Selecione o bairro")
        if not ed_cep:
            raise ValidationError("informe o cep")
        if not ed_logradouro:
            raise ValidationError("Informe o logradouro")
        
        bairro_valido = _existe_bairro(ed_bairro)
        if bairro_valido:
            _valida_cidade_estado_pais(bairro_valido, ed_cidade, ed_estado, ed_pais)

        endereco.bairro = bairro_valido
        endereco.cep = ed_cep
        endereco.logradouro = ed_logradouro
        endereco.numero = ed_numero
        endereco.complemento = ed_complemento
        endereco.descricao = ed_descricao

    else:
        if not ed_descricao:
            raise ValidationError("Informe a descrição/referência do endereço")

    endereco.save()
    return endereco

#########
#funções internas
#########
def _valida_cidade(id:int)->Cidade:
    try:
        return Cidade.objects.get(pk=id)
    except Cidade.DoesNotExist:
            raise ValidationError("Cidade inválida")

def _valida_estado(id:int)->Estado:
    try:
        return Estado.objects.get(pk=id)
    except Estado.DoesNotExist:
            raise ValidationError("Estado não cadastrado")

def _valida_cidade_estado_pais(bairro:Bairro, idcidade:int, idestado:int, idpais:int)->None:
    existe = Bairro.objects.filter(
        cidade_id = idcidade,
        cidade__estado_id=idestado,
        cidade__estado__pais_id = idpais
    ).exists()
    if not existe:
        raise ValidationError("O bairro não pertence à cidade, estado ou país informado.")

def _existe_bairro(id:int)->Bairro:
    try:
        return Bairro.objects.get(pk=id)
    except Bairro.DoesNotExist:
        raise ValidationError("Bairro não encontrado")

def _existe_endereco(end:int)->Endereco:
    try:
        return Endereco.objects.get(pk=end)
    except Endereco.DoesNotExist:
        raise ValidationError("Pessoa não foi encontrada")
    
def buscar_endereco_cep(cep):
    cep_limpo = _limpar_cep(cep)
    url = f"https://viacep.com.br/ws/{cep_limpo}/json/"
    consulta = requests.get(url)
    if consulta.status_code != 200:
        return None
    
    data = consulta.json()
    if data.get("erro"):
        return None

    return {
        "cep": data.get("cep"),
        "estado": data.get("uf"),
        "cidade": data.get("localidade"),
        "bairro": data.get("bairro"),
        "logradouro": data.get("logradouro"),
    }

def _limpar_cep(cep: str)-> str:
    cep_limpo = re.sub(r"\D", "", cep)
    if len(cep_limpo) != 8:
        raise ValidationError (f"CEP '{cep}' é inválido. Deve conter 8 dígitos.")
    return cep_limpo


