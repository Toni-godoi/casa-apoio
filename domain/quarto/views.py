from django.shortcuts import render, redirect, get_object_or_404
from domain.quarto.models import Quarto

# Create your views here.
def listar_quartos_view(request):

    quartos = Quarto.objects.all()

    return render(
        request,
        "quarto/listar_quartos.html",
        {"quartos": quartos}
    )

def detalhe_quarto_view(request, pk):

    quarto = get_object_or_404(Quarto, pk=pk)

    alocacoes_ativas = quarto.quarto_alocacao.filter(
        fimLocacao__isnull=True
    )

    historico = quarto.quarto_alocacao.all().order_by(
        "-inicioLocacao"
    )

    return render(
        request,
        "quarto/detalhe_quarto.html",
        {
            "quarto": quarto,
            "alocacoes_ativas": alocacoes_ativas,
            "historico": historico,
        }
    )