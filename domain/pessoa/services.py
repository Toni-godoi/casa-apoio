from typing import Optional
from django.db import transaction
from django.utils import timezone
from validate_docbr import CPF
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from datetime import date, time, datetime, timedelta
from domain.pessoa.models import Pessoa, PessoaEditada, FotoPerfilPessoa
from domain.endereco.models import Endereco

@transaction.atomic
def cadastrar_pessoa(
    *,
    nome_pessoa:str,
    cpf_pessoa:str,
    sexo_pessoa:str,
    dataNasc_pessoa:date,
    nacionalidade_pessoa:str,
    telefone_pessoa:str,
    email_pessoa:Optional[str]=None,
    descricao_pessoa:Optional[str]=None,
    endereco_pessoa=Endereco,
    foto_perfil=None
)->Pessoa:
    
    nome_pessoa = _valida_nome(nome_pessoa)
    cpf_pessoa = _valida_cpf(cpf_pessoa)
    dataNasc_pessoa = _valida_dataNasc(dataNasc_pessoa)
    telefone_pessoa = _valida_telefone(telefone_pessoa)
    if email_pessoa:
        email_pessoa = _valida_email(email_pessoa)
    cadastro = timezone.localdate()
    
    if endereco_pessoa is None:
        raise ValidationError("Endereço não informado")
    endereco = _valida_endereco(endereco_pessoa)

    pessoa = Pessoa(
        nome_pessoa = nome_pessoa,
        cpf_pessoa = cpf_pessoa,
        sexo_pessoa = sexo_pessoa,
        dataNasc_pessoa = dataNasc_pessoa,
        nacionalidade_pessoa = nacionalidade_pessoa,
        telefone_pessoa = telefone_pessoa,
        dataCadastro = cadastro,
        email_pessoa = email_pessoa,
        descricao_pessoa = descricao_pessoa,
        endereco = endereco
    )
    pessoa.save()

    if foto_perfil:
        foto = FotoPerfilPessoa(
            pessoa = pessoa,
            arquivo = foto_perfil
        )
        foto.save()
    return pessoa

@transaction.atomic
def editar_pessoa(
    *,
    ed_pessoa_id:int,
    ed_nome_pessoa:str,
    ed_cpf_pessoa:str,
    ed_sexo_pessoa:str,
    ed_dataNasc_pessoa:date,
    ed_nacionalidade_pessoa:str,
    ed_telefone_pessoa:str,
    ed_email_pessoa:Optional[str]=None,
    ed_descricao_pessoa:Optional[str]=None,
    ):

    #valida se a pessoa informada existe
    pessoa = _existe_pessoa(ed_pessoa_id)

    #registra os capos que foram alterados e valida dados
    campos_alterados = []

    if pessoa.nome_pessoa != ed_nome_pessoa:
        ed_nome_pessoa = _valida_nome(ed_nome_pessoa)
        campos_alterados.append("Nome")
        pessoa.nome_pessoa = ed_nome_pessoa

    cpf_normalizado = ''.join(filter(str.isdigit, ed_cpf_pessoa))
    if pessoa.cpf_pessoa != cpf_normalizado:
        ed_cpf_pessoa = _valida_cpf(cpf_normalizado)
        campos_alterados.append("CPF")
        pessoa.cpf_pessoa = ed_cpf_pessoa

    if pessoa.dataNasc_pessoa != ed_dataNasc_pessoa:
        ed_dataNasc_pessoa = _valida_dataNasc(ed_dataNasc_pessoa)
        campos_alterados.append("Data de Nascimento")
        pessoa.dataNasc_pessoa = ed_dataNasc_pessoa

    if pessoa.sexo_pessoa != ed_sexo_pessoa:
        campos_alterados.append("Sexo")
        pessoa.sexo_pessoa = ed_sexo_pessoa
    
    if pessoa.nacionalidade_pessoa != ed_nacionalidade_pessoa:
        campos_alterados.append("Sexo")
        pessoa.nacionalidade_pessoa = ed_nacionalidade_pessoa

    tel_normalizado = ''.join(filter(str.isdigit, ed_telefone_pessoa))
    if pessoa.telefone_pessoa != tel_normalizado:
        ed_telefone_pessoa = _valida_telefone(tel_normalizado)
        campos_alterados.append("Telefone")
        pessoa.telefone_pessoa = ed_telefone_pessoa

    if pessoa.email_pessoa != ed_email_pessoa:
        if ed_email_pessoa != "":
            ed_email_pessoa = _valida_email(ed_email_pessoa)
        
        campos_alterados.append("Email")
        pessoa.email_pessoa = ed_email_pessoa
    
    if pessoa.descricao_pessoa != ed_descricao_pessoa:
        campos_alterados.append("Outras Informações")
        pessoa.descricao_pessoa = ed_descricao_pessoa

    pessoa.save()

    #registra os campos modificados na tabela de dados do usuário modificados
    if campos_alterados:
        edicao = timezone.localdate()
        PessoaEditada.objects.create(
            pessoa = pessoa,
            camposAlterados = campos_alterados,
            dataEdicao = edicao
        )
    return pessoa

def _valida_endereco(endereco:Endereco)->Endereco:
    if not isinstance(endereco, Endereco):
        raise ValidationError("Endereço inválido ou nao cadastrado")
    return endereco

def _existe_pessoa(pessoa_pk:int)->Pessoa:
    try:
        return Pessoa.objects.get(pk=pessoa_pk)
    except Pessoa.DoesNotExist:
        raise ValidationError("Pessoa não foi encontrada")

def _valida_email(email:str)->str:
    try:
        validate_email(email)
    except:
        raise ValidationError("email invalido")
    return email

def _valida_telefone(telefone:str)->str:

    tel = ''.join(filter(str.isdigit, telefone))
    if len(tel) not in [10,11]:
        raise ValidationError("Telefone invalido")
    return tel

def _valida_dataNasc(data:date)->date:
    nascimento = data
    hoje = timezone.localdate()
    idade = hoje.year - nascimento.year

    if nascimento > hoje:
        raise ValidationError("data de nascimento invalida")
    if idade > 120:
        raise ValidationError(f"a idade {idade} não é valida")
    
    return nascimento

def _valida_cpf(cpf:str)->str:

    cpf_valido = ''.join(filter(str.isdigit, cpf))
    if len(cpf_valido)!=11:
        raise ValidationError("CPF invalido")
    
    if Pessoa.objects.filter(cpf_pessoa=cpf_valido).exists():
        raise ValidationError("CPF ja esta cadastrado")
    
    validador = CPF()
    if not validador.validate(cpf_valido):
        raise ValidationError("CPF invalido")
    
    return cpf_valido

def _valida_nome(nome=str)->str:
    nome = nome.strip()
    if len(nome)<3:
        raise ValidationError("nome precisa de ao menos 3 caracteres")
    
    return nome