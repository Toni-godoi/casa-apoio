from django.shortcuts import render
from django.contrib import messages
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from domain.pessoa.forms import CadastrarEditarPessoaForm
from domain.pessoa.utils import calcular_idade
from domain.pessoa.models import Pessoa, FotoPerfilPessoa, PessoaEditada
from domain.pessoa.services import cadastrar_pessoa, editar_pessoa
from domain.endereco.forms import BrasilEndercoForm
from domain.endereco.services import cadastrar_endereco, buscar_endereco_cep, editar_endereco
from domain.apoio.models import Apoio

# Create your views here.
@login_required
def cadastrar_pessoa_view(request):
    
    form = CadastrarEditarPessoaForm(request.POST or None, request.FILES or None)
    form_end = BrasilEndercoForm(request.POST or None)
    idade = None

    if request.method == "POST" and form.is_valid() and form_end.is_valid():
    
        data_nascimento = form.cleaned_data['dataNasc_pessoa']
        idade = calcular_idade(data_nascimento)
        foto_pessoa = form.cleaned_data.get("foto")
        
        cd = form.cleaned_data
        cd_end = form_end.cleaned_data
        try:
            endereco = cadastrar_endereco(
                pais = cd_end['pais'],
                cep = cd_end['cep'],
                estado = cd_end['estado'],
                cidade = cd_end['cidade'],
                bairro = cd_end['bairro'],
                logradouro = cd_end['logradouro'],
                numero = cd_end['numero'],
                complemento = cd_end['complemento'],
                descricao = cd_end['descricao']
            )
            pessoa = cadastrar_pessoa(
                nome_pessoa=cd['nome_pessoa'],
                cpf_pessoa=cd["cpf_pessoa"],
                sexo_pessoa=cd['sexo_pessoa'],
                dataNasc_pessoa=cd['dataNasc_pessoa'],
                nacionalidade_pessoa=cd['nacionalidade_pessoa'],
                telefone_pessoa=cd['telefone_pessoa'],
                email_pessoa=cd['email_pessoa'],
                descricao_pessoa=cd['descricao_pessoa'],
                foto_perfil = foto_pessoa,
                endereco_pessoa = endereco
            )
            return redirect ("pessoa:dados_pessoa", pessoa.pk)
        
        except ValidationError as exc:
            for msg in exc.messages:
                messages.error(request, msg)

    return render(request, "pessoa/cadastrar_pessoa.html", {
        "form": form,
        "form_end": form_end,
        "idade": idade})

@login_required
def dados_pessoa_view(request, pk):
    pessoa = get_object_or_404(Pessoa, pk=pk)

    apoios=[]
    for apoio in pessoa.pacientes.all():
        apoios.append({
            "apoio": apoio,
            "participacao": "Paciente",
            "checkin": apoio.checkIn,
            "checkout": apoio.checkOut})
        
    for apoio in Apoio.objects.filter(solicitante__pessoa=pessoa):
        apoios.append({
            "apoio": apoio,
            "participacao": "Solicitante",
            "checkin": None,
            "checkout": None})
        
    for acomp in pessoa.vinculos_acompanhantes.all():
        apoios.append({
            "apoio": acomp.apoio,
            "participacao": "Acompanhante",
            "checkin": acomp.checkIn,
            "checkout": acomp.checkOut,})

    apoios.sort(
        key=lambda x: x["apoio"].dataInicio,
        reverse=True)

    return render(request, "pessoa/dados_pessoa.html", {
        "pessoa": pessoa,
        "apoios": apoios})

@login_required
def listar_pessoas_views(request):

    nome = request.GET.get("nome")
    cpf = request.GET.get("cpf")
    telefone = request.GET.get("telefone")
    email = request.GET.get("email")
    data_inicio = request.GET.get("data_inicio")
    data_fim = request.GET.get("data_fim")

    pessoas = Pessoa.objects.none()
    if any([nome, cpf, telefone, email, data_inicio, data_fim]):
        pessoas = Pessoa.objects.all()
        if nome:
            pessoas = pessoas.filter(nome_pessoa__icontains=nome)
        if cpf:
            cpf = ''.join(filter(str.isdigit, cpf))
            pessoas = pessoas.filter(cpf_pessoa__icontains=cpf)
        if telefone:
            pessoas = pessoas.filter(telefone_pessoa__icontains=telefone)
        if email:
            pessoas = pessoas.filter(email_pessoa__icontains=email)
        if data_inicio and data_fim:
            data_inicio_dt = datetime.strptime(data_inicio, "%Y-%m-%d").date()
            data_fim_dt = datetime.strptime(data_fim, "%Y-%m-%d").date()
            diferenca = (data_fim_dt - data_inicio_dt).days
            try:
                if diferenca>90:
                    raise ValidationError("Escolha um periodo menor que 90 dias")
                if diferenca <0:
                    raise ValidationError("Periodo de cadastro invalido")
                pessoas = pessoas.filter(dataCadastro__range=[data_inicio,data_fim])
            except ValidationError as exc:
                messages.error(request, exc.messages[0])

    return render(request,"pessoa/listar_pessoas.html",{"pessoas": pessoas})

@login_required
def editar_pessoa_view(request, pk):
    pessoa = get_object_or_404(Pessoa, pk=pk)

    initial = {
        'nome_pessoa': pessoa.nome_pessoa,
        'cpf_pessoa':pessoa.cpf_pessoa,
        'sexo_pessoa':pessoa.sexo_pessoa,
        'dataNasc_pessoa':pessoa.dataNasc_pessoa.strftime("%Y-%m-%d"),
        'nacionalidade_pessoa':pessoa.nacionalidade_pessoa,
        'telefone_pessoa':pessoa.telefone_pessoa,
        'email_pessoa':pessoa.email_pessoa,
        'descricao_pessoa':pessoa.descricao_pessoa,
        #endereços:
        'pais':pessoa.endereco.pais,
        'cep':pessoa.endereco.cep,
        'estado':pessoa.endereco.estado,
        'cidade':pessoa.endereco.cidade,
        'bairro':pessoa.endereco.bairro,
        'logradouro':pessoa.endereco.logradouro,
        'numero':pessoa.endereco.numero,
        'complemento':pessoa.endereco.complemento,
        'descricao':pessoa.endereco.descricao,
    }

    form = CadastrarEditarPessoaForm(request.POST or None, initial=initial)
    form_end = BrasilEndercoForm(request.POST or None, initial=initial)
    
    if request.method == "POST" and form.is_valid() and form_end.is_valid():
        cd = form.cleaned_data
        cd_end = form_end.cleaned_data

        try:
            endereco = editar_endereco(
                ed_endereco_id=pessoa.endereco.pk,
                ed_pais = cd_end['pais'],
                ed_cep = cd_end['cep'],
                ed_estado = cd_end['estado'],
                ed_cidade = cd_end['cidade'],
                ed_bairro = cd_end['bairro'],
                ed_logradouro = cd_end['logradouro'],
                ed_numero = cd_end['numero'],
                ed_complemento = cd_end['complemento'],
                ed_descricao = cd_end['descricao']
            )
            pessoa = editar_pessoa(
                ed_pessoa_id=pessoa.pk,
                ed_nome_pessoa=cd['nome_pessoa'],
                ed_cpf_pessoa=cd["cpf_pessoa"],
                ed_sexo_pessoa=cd['sexo_pessoa'],
                ed_dataNasc_pessoa=cd['dataNasc_pessoa'],
                ed_nacionalidade_pessoa=cd['nacionalidade_pessoa'],
                ed_telefone_pessoa=cd['telefone_pessoa'],
                ed_email_pessoa=cd['email_pessoa'],
                ed_descricao_pessoa=cd['descricao_pessoa']
            )
            return redirect ("pessoa:dados_pessoa", pessoa.pk)
        
        except ValidationError as exc:
            for msg in exc.messages: messages.error(request, msg)

    return render(request, "pessoa/editar_pessoa.html", {
        "form": form,
        "form_end": form_end, 
        "pessoa":pessoa})



