from django.contrib import messages
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from domain.quarto.models import Quarto
from domain.quarto.services import cadastrar_quarto, editar_quarto, desativar_quarto
from domain.quarto.forms import QuartoForm

# Create your views here.
@login_required
def cadastrar_quarto_view(request):

    form = QuartoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        cd = form.cleaned_data
        try:
            quarto = cadastrar_quarto(
                identificacao=cd['identificacao'],
                quantidadeVagas=cd['quantidadeVagas']
            )
            return redirect ("quarto:detalhe_quarto", quarto.pk)
        
        except ValidationError as exc:
            for msg in exc.messages:
                messages.error(request, msg)

    return render(request, "quarto/cadastrar_quarto.html", {"form": form,})

@login_required
def listar_quartos_desativados_view(request):
    quartos = Quarto.objects.filter(status=False)
    return render(request, "quarto/quartos_desativados.html",{"quartos": quartos})

@login_required
def listar_quartos_ativos_view(request):
    quartos = Quarto.objects.filter(status=True)
    return render(request,"quarto/quartos_ativos.html",{"quartos": quartos})

@login_required
def detalhe_quarto_view(request, pk):
    quarto = get_object_or_404(Quarto, pk=pk)

    alocacoes_ativas = quarto.quarto_alocacao.filter(fimLocacao__isnull=True)
    historico = quarto.quarto_alocacao.all().order_by("-inicioLocacao")

    return render(request,"quarto/detalhe_quarto.html",
        {
            "quarto": quarto,
            "alocacoes_ativas": alocacoes_ativas,
            "historico": historico,
        }
    )