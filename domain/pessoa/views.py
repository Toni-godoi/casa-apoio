from django.shortcuts import render
from django.contrib import messages
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from domain.pessoa.forms import CadastrarEditarPessoaForm
from domain.pessoa.utils import calcular_idade
from domain.pessoa.models import Pessoa, PessoaEditada
from domain.pessoa.services import cadastrar_pessoa, editar_pessoa

# Create your views here.
@login_required
def cadastrar_pessoa_view(request):

    form = CadastrarEditarPessoaForm(request.POST or None)

    idade = None

    if request.method == "POST" and form.is_valid():

        data_nascimento = form.cleaned_data['dataNasc_pessoa']
        idade = calcular_idade(data_nascimento)
        
        cd = form.cleaned_data
        try:
            pessoa = cadastrar_pessoa(
                nome_pessoa=cd['nome_pessoa'],
                cpf_pessoa=cd["cpf_pessoa"],
                sexo_pessoa=cd['sexo_pessoa'],
                dataNasc_pessoa=cd['dataNasc_pessoa'],
                nacionalidade_pessoa=cd['nacionalidade_pessoa'],
                telefone_pessoa=cd['telefone_pessoa'],
                email_pessoa=cd['email_pessoa'],
                descricao_pessoa=cd['descricao_pessoa']
            )
            return redirect ("pessoa:dados_pessoa", pessoa.pk)
        
        except ValidationError as exc:
            for msg in exc.messages:
                messages.error(request, msg)

    return render(request, "pessoa/cadastrar_pessoa.html", {
        "form": form,
        "idade": idade})

@login_required
def dados_pessoa_view(request, pk):
    pessoa = get_object_or_404(Pessoa, pk=pk)
    return render(request, "pessoa/dados_pessoa.html", {"pessoa": pessoa})

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
        'descricao_pessoa':pessoa.descricao_pessoa
    }

    form = CadastrarEditarPessoaForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        cd = form.cleaned_data

        try:
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

    return render(request, "pessoa/editar_pessoa.html", {"form": form, "pessoa":pessoa})



