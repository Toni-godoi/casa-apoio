from django.shortcuts import render
from django.contrib import messages
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET, require_http_methods
from domain.endereco.services import buscar_endereco_cep, cadastrar_cidade, cadastrar_bairro, editar_bairro
from domain.endereco.models import Estado, Pais, Cidade, Bairro
from domain.endereco.forms import CadastrarCidade, CadastrarEditarBairro

@login_required
def w_cadastrar_bairro(request, pk):

    cidade = get_object_or_404(Cidade, pk=pk)
    form = CadastrarEditarBairro(request.POST or None)

    if request.method == "POST" and form.is_valid():
        cd = form.cleaned_data
        try:
            bairro = cadastrar_bairro(
                cidade = cidade.pk,
                bairro = cd['bairro']
            )
            return redirect ("endereco:listar_bairros", pk=cidade.pk)
        
        except ValidationError as exc:
                for msg in exc.messages:
                    messages.error(request, msg)

    return render(request, "endereco/cadastrar_bairro.html", {"form":form, "cidade": cidade})

@login_required
def w_editar_bairro(request, pk, pk_bairro):
    cidade = get_object_or_404(Cidade, pk=pk)
    bairro = get_object_or_404(Bairro, pk=pk_bairro, cidade=cidade)

    initial = {'bairro' : bairro}
    form = CadastrarEditarBairro(request.POST or None, initial=initial)

    if request.method == "POST" and form.is_valid():
        cd = form.cleaned_data
        try:
            bairro = editar_bairro(
                bairro_id = bairro.pk,
                ed_bairro = cd['bairro']
            )
            return redirect ("endereco:listar_bairros", pk=cidade.pk)
        
        except ValidationError as exc:
                for msg in exc.messages:
                    messages.error(request, msg)

    return render(request, "endereco/cadastrar_bairro.html", {"form":form, "bairro":bairro, "cidade": cidade})

@login_required
def w_cadastrar_cidade(request):

    form = CadastrarCidade(request.POST or None)

    if request.method == "POST" and form.is_valid():
        cd = form.cleaned_data
        try:
            cidade = cadastrar_cidade(
                estado = cd['estado'].pk,
                cidade = cd['cidade']
            )
            return redirect ("endereco:listar_enderecos")
        
        except ValidationError as exc:
                for msg in exc.messages:
                    messages.error(request, msg)

    estados = list(Estado.objects.values("id", "pais"))
    return render(request, "endereco/cadastrar_cidade.html", {"form":form,"estados":estados})

def listar_estados(request):
    paises = Pais.objects.all().order_by("pais")
    estados = Estado.objects.all().order_by("pais__pais", "estado")
    cidades = Cidade.objects.all().order_by("estado__pais__pais", "estado__estado", "cidade")

    return render(request, 
                  "endereco/listar_cidades.html",
                  {"paises": paises,
                   "estados": estados,
                   "cidades": cidades})

def listar_bairros(request, pk):
    cidade = get_object_or_404(Cidade, pk=pk)
    bairros = cidade.cidade_bairro.all().order_by("bairro")

    return render(request, 
                  "endereco/listar_bairros.html",
                  {"bairros": bairros,
                   "cidade": cidade,})

    