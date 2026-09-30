import re
import requests
import urllib.error
import urllib.request
import json
from django.db import transaction
from dataclasses import dataclass
from django.core.exceptions import ValidationError
from django.db.models.functions import Lower, Trim
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
        nome_bairro = bairro
    )
    bairro.save()
    return bairro

@transaction.atomic
def editar_bairro(
    *,
    ed_bairro=str,
    bairro_id = int
)->Bairro:

    bairro_valido = _valida_bairro(bairro_id)

    if bairro_valido.nome_bairro != ed_bairro:
        bairro_valido.nome_bairro = ed_bairro

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
        nome_cidade = cidade
    )
    cidade.save()
    return cidade

@transaction.atomic
def cadastrar_end_pessoa(
    *,
    pais:int,
    estado:str,
    uf_estado:str,
    cidade:str,
    bairro:str,
    cep:int,
    logradouro:str,
    numero:Optional[int]=None,
    complemento:Optional[str]=None,
    descricao:Optional[str]=None,
)->Endereco:

    pais_valido = _valida_pais(pais)    
    if pais_valido.nome_pais == "Brasil":
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

    estado_encontrado = _existe_estado(estado, uf_estado)
    if not estado_encontrado:
        estado = Estado(
            nome_estado = estado,
            uf_estado = uf_estado,
            pais = pais_valido
        )
        estado.save()
        estado_encontrado = estado

    cidade_encontrada = _existe_cidade(cidade, estado_encontrado.pk)
    if not cidade_encontrada:
        cidade = Cidade(
            nome_cidade = cidade,
            estado = estado_encontrado
        )
        cidade.save()
        cidade_encontrada = cidade

    bairro_encontrado = _existe_bairro(bairro, cidade_encontrada.pk, estado_encontrado.pk)
    if not bairro_encontrado:
        bairro = Bairro(
            nome_bairro = bairro,
            cidade = cidade_encontrada
        )
        bairro.save()
        bairro_encontrado = bairro
    
    endereco = Endereco(
        numero = numero,
        complemento = complemento,
        logradouro = logradouro,
        descricao = descricao,
        cep = cep,
        bairro = bairro_encontrado
    )
    endereco.save()
    return endereco
    
@transaction.atomic
def editar_end_pessoa(
    *,
    ed_endereco_id:int,
    ed_pais:int,
    ed_cep:Optional[int]=None,
    ed_estado:str,
    ed_uf_estado:str,
    ed_cidade:str,
    ed_bairro:str,
    ed_logradouro:Optional[str]=None,
    ed_numero:Optional[int]=None,
    ed_complemento:Optional[str]=None,
    ed_descricao:Optional[str]=None,
    ):

    endereco = _valida_endereco(ed_endereco_id)
    pais_valido = _valida_pais(ed_pais)
    if pais_valido.nome_pais == "Brasil":
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
        
    estado_encontrado = _existe_estado(ed_estado, ed_uf_estado)
    if not estado_encontrado:
        estado = Estado(
            nome_estado = ed_estado,
            uf_estado = ed_uf_estado,
            pais = pais_valido
        )
        estado.save()
        estado_encontrado = estado

    cidade_econtrada = _existe_cidade(ed_cidade, estado_encontrado.pk)
    if not cidade_econtrada:
        cidade = Cidade(
            nome_cidade = ed_cidade,
            estado = estado_encontrado
        )
        cidade.save()
        cidade_econtrada = cidade

    bairro_encontrado = _existe_bairro(ed_bairro, cidade_econtrada.pk, estado_encontrado.pk)
    if not bairro_encontrado:
        bairro = Bairro(
            nome_bairro = ed_bairro,
            cidade = cidade_econtrada
        )
        bairro.save()
        bairro_encontrado = bairro

    if endereco.cep != ed_cep:
        endereco.cep = ed_cep
    if endereco.numero != ed_numero:
        endereco.numero = ed_numero
    if endereco.logradouro != ed_logradouro:
        endereco.logradouro = ed_logradouro
    if endereco.complemento != ed_complemento:
        endereco.complemento = ed_complemento
    if endereco.descricao != ed_descricao:
        endereco.descricao = ed_descricao

    if endereco.bairro.cidade.estado.pais != pais_valido:
        endereco.bairro.cidade.estado.pais = pais_valido
    if endereco.bairro.cidade.estado != estado_encontrado:
        endereco.bairro.cidade.estado = estado_encontrado
    if endereco.bairro.cidade != cidade_econtrada:
        endereco.bairro.cidade = cidade_econtrada
    if endereco.bairro != bairro_encontrado:
        endereco.bairro = bairro_encontrado

    endereco.save()
    return endereco

#########
#funções que verificam se há ou não registros e retornam V/F
#########
def _existe_estado(nome:str, uf:str)->Estado | None:
    return Estado.objects.filter(nome_estado = nome, uf_estado=uf).first()

def _existe_cidade(cidade:str, estadoId:int)->Cidade | None:
    return Cidade.objects.filter(nome_cidade=cidade, estado_id=estadoId).first()

def _existe_bairro(bairro:str, cidadeId:int, estadoId:int)->Bairro | None:
    return Bairro.objects.filter(nome_bairro=bairro, cidade_id=cidadeId, cidade__estado_id=estadoId).first()

#########
#funções que consultam registros que ja devem ser existes e retorna erro se não econtrar
#########
def _valida_pais(id:int)->Pais:
    try:
        return Pais.objects.get(pk=id)
    except Pais.DoesNotExist:
        raise ValidationError("Pais inválido")

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

def _valida_bairro(id:int)->Bairro:
    try:
        return Bairro.objects.get(pk=id)
    except Bairro.DoesNotExist:
        raise ValidationError("Bairro não encontrado")

def _valida_endereco(end:int)->Endereco:
    try:
        return Endereco.objects.get(pk=end)
    except Endereco.DoesNotExist:
        raise ValidationError("Endereço não foi encontrado")


#########
#funções de busca endereços correios
#########
def _buscar_endereco_cep(cep):
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
        "uf": data.get("uf"),
        "estado": data.get("estado"),
        "cidade": data.get("localidade"),
        "bairro": data.get("bairro"),
        "logradouro": data.get("logradouro"),
    }

def _limpar_cep(cep: str)-> str:
    cep_limpo = re.sub(r"\D", "", cep)
    if len(cep_limpo) != 8:
        raise ValidationError (f"CEP '{cep}' é inválido. Deve conter 8 dígitos.")
    return cep_limpo