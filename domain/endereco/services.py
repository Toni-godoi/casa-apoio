import re
import requests
import urllib.error
import urllib.request
import json
from django.db import transaction
from dataclasses import dataclass
from django.core.exceptions import ValidationError
from typing import Optional
from domain.endereco.models import Endereco

@transaction.atomic
def cadastrar_endereco(
    *,
    pais:str,
    cep:Optional[int]=None,
    estado:Optional[str]=None,
    cidade:Optional[str]=None,
    bairro:Optional[str]=None,
    logradouro:Optional[str]=None,
    numero:Optional[int]=None,
    complemento:Optional[str]=None,
    descricao:Optional[str]=None,
)->Endereco:
    
    if pais == 'BR':
        if not cep:
            raise ValidationError("cep é obrigatório")
        if not estado:
             raise ValidationError("Estado é obrigatório")
        if not cidade:
             raise ValidationError("Cidade é obrigatório")
        if not bairro:
             raise ValidationError("Bairro é obrigatório")
        if not logradouro:
             raise ValidationError("Logradouro é obrigatório")
    if pais != 'BR':
        if not descricao:
             raise ValidationError("Forneça uma descrição para o endereço estrangeiro")

    endereco = Endereco(
        pais = pais,
        cep = cep,
        estado = estado,
        cidade = cidade,
        bairro = bairro,
        logradouro = logradouro,
        numero = numero,
        complemento = complemento,
        descricao = descricao
    )

    endereco.save()
    return endereco

@transaction.atomic
def editar_endereco(
    *,
    ed_endereco_id:int,
    ed_pais:str,
    ed_cep:Optional[int]=None,
    ed_estado:Optional[str]=None,
    ed_cidade:Optional[str]=None,
    ed_bairro:Optional[str]=None,
    ed_logradouro:Optional[str]=None,
    ed_numero:Optional[int]=None,
    ed_complemento:Optional[str]=None,
    ed_descricao:Optional[str]=None,
    ):

    endereco = _existe_endereco(ed_endereco_id)
    
    if endereco.pais != ed_pais:
        endereco.pais = ed_pais
    if endereco.cep != ed_cep:
        endereco.cep = ed_cep
    if endereco.estado != ed_estado:
        endereco.estado = ed_estado
    if endereco.cidade != ed_cidade:
        endereco.cidade = ed_cidade
    if endereco.bairro != ed_bairro:
        endereco.bairro = ed_bairro
    if endereco.logradouro != ed_logradouro:
        endereco.logradouro = ed_logradouro
    if endereco.numero != ed_numero:
        endereco.numero = ed_numero
    if endereco.complemento != ed_complemento:
        endereco.complemento = ed_complemento
    if endereco.descricao != ed_descricao:
        endereco.descricao = ed_descricao
    
    endereco.save()

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

def _existe_endereco(end:int)->Endereco:
    try:
        return Endereco.objects.get(pk=end)
    except Endereco.DoesNotExist:
        raise ValidationError("Pessoa não foi encontrada")

def _limpar_cep(cep: str)-> str:
    cep_limpo = re.sub(r"\D", "", cep)
    if len(cep_limpo) != 8:
        raise ValidationError (f"CEP '{cep}' é inválido. Deve conter 8 dígitos.")
    return cep_limpo
