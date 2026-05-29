from django.shortcuts import render
from django.contrib import messages
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from domain.solicitacao.models import SolicitantePessoa, FuncaoSolicitantePessoa
from domain.solicitacao.services import cadastrar_funcao_pessoa, editar_funcao_pessoa, excluir_funcao_pessoa, cadastrar_solicitante_pessoa, editar_solicitante_pessoa
from domain.solicitacao.forms import CadastrarFuncaoForm, CadastrarSolicitantePessoaForm
from domain.pessoa.models import Pessoa

# Create your views here.
@login_required
def cadastrar_funcao_view(request):
    form = CadastrarFuncaoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        cd = form.cleaned_data
        try:
            funcao_pessoa = cadastrar_funcao_pessoa(
                funcao=cd['funcao'],
                descricao=cd['descricao']
            )
            return redirect ("solicitacao:listar_funcoes")
        except ValidationError as exc:
            for msg in exc.messages:
                messages.error(request, msg)
    return render(request, "solicitacao/cadastrar_funcao.html", {"form": form,})

@login_required
def listar_funcoes_view(request):
    funcoes = FuncaoSolicitantePessoa.objects.all()
    return render(request,"solicitacao/listar_funcoes.html",{"funcoes": funcoes})

@login_required
def excluir_funcao_view(request, pk):
    try:
        excluir_funcao_pessoa(funcao_id=pk)
    except ValidationError as exc:
        messages.error(request,exc.messages[0])
    return redirect("solicitacao:listar_funcoes")

@login_required
def dados_funcao_view(request, pk):
    funcao = get_object_or_404(FuncaoSolicitantePessoa, pk=pk)
    return render(request, "solicitacao/dados_funcao.html", {"funcao": funcao})

@login_required
def editar_funcao_view(request, pk):
    funcao = get_object_or_404(FuncaoSolicitantePessoa, pk=pk)
    initial = {
        'funcao':funcao.funcao,
        'descricao':funcao.descricao
    }
    form = CadastrarFuncaoForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        cd = form.cleaned_data
        try:
            funcao = editar_funcao_pessoa(
                ed_funcao_id = funcao.pk,
                ed_funcao = cd['funcao'],
                ed_descricao = cd['descricao']
            )
            return redirect ("solicitacao:listar_funcoes")
        
        except ValidationError as exc:
            for msg in exc.messages: messages.error(request, msg)

    return render(request, "solicitacao/editar_funcao.html", {"form": form, "funcao":funcao})

@login_required
def cadastrar_solicitante_view(request):
    
    pessoas = Pessoa.objects.all()
    funcoes = FuncaoSolicitantePessoa.objects.all()

    form = CadastrarSolicitantePessoaForm(request.POST or None)

    form.fields["pessoa"].choices = [(p.id, p.nome_pessoa)for p in pessoas]
    form.fields["funcao"].choices = [(p.id, p.funcao)for p in funcoes]

    if request.method == "POST" and form.is_valid():
        cd = form.cleaned_data
        try:
            cadastrar_solicitante_pessoa(
                pessoa_id = cd['pessoa'],
                funcao_id = cd['funcao'],
                descricao=cd['descricao']
            )
            return redirect ("solicitacao:listar_solicitantes")
        
        except ValidationError as exc:
            for msg in exc.messages:
                messages.error(request, msg)

    return render(request, "solicitacao/cadastrar_solicitante.html", 
                  {"form": form})

@login_required
def listar_solicitantes_view(request):
    solicitantes = SolicitantePessoa.objects.all()
    return render(request,"solicitacao/listar_solicitantes.html",{"solicitantes": solicitantes})

@login_required
def editar_solicitante_view(request, pk):
    solicitante = get_object_or_404(SolicitantePessoa, pk=pk)
    
    pessoas = Pessoa.objects.all()
    funcoes = FuncaoSolicitantePessoa.objects.all()

    initial = {
        'pessoa':solicitante.pessoa,
        'funcao':solicitante.funcao,
        'descricao':solicitante.descricao
    }
    form = CadastrarSolicitantePessoaForm(request.POST or None, initial=initial)

    form.fields["pessoa"].choices = [(p.id, p.nome_pessoa)for p in pessoas]
    form.fields["funcao"].choices = [(p.id, p.funcao)for p in funcoes]

    if request.method == "POST" and form.is_valid():
        cd = form.cleaned_data
        try:
            solicitante_pessoa = editar_solicitante_pessoa(
                ed_solicitante_id = solicitante.pk,
                ed_pessoa_id = cd['pessoa'],
                ed_funcao_id = cd['funcao'],
                ed_descricao = cd['descricao']
            )
            return redirect ("solicitacao:listar_solicitantes")
        
        except ValidationError as exc:
            for msg in exc.messages: messages.error(request, msg)

    return render(request, "solicitacao/editar_solicitante.html", {"form": form, "solicitante":solicitante})