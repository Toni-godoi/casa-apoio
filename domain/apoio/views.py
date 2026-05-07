from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError

from domain.apoio.forms import IniciarApoioForm, AdicionarAcompanhante, EditarApoioForm
from domain.apoio.models import Apoio
from domain.quarto.models import Quarto
from domain.apoio.services import iniciar_apoio, editar_apoio, vincular_acompanhante, checkout_acompanhante, checkIn_apoio, checkOut_apoio

# Create your views here.
def iniciar_apoio_view(request):

    quarto_id = request.GET.get("quarto_id")
    quarto_obj = None

    form = IniciarApoioForm(request.POST or None)

    if quarto_id and request.method != "POST":
        form.initial["quarto"] = quarto_id
        quarto_obj = Quarto.objects.filter(pk=quarto_id).first()

    tipo = None

    if request.method == "POST":
        tipo = request.POST.get("previsaoFim_tipo")
    else:
        tipo = request.GET.get("previsaoFim_tipo")

    precisa_hospedagem = tipo in ["INDETERMINADO", "DATA"]

    if request.method == "POST" and form.is_valid():
        cd = form.cleaned_data
        try:
            apoio = iniciar_apoio(
                #casa_apoio
                motivo_apoio=cd["motivo_apoio"],
                data_inicio=cd["data_inicio"],
                previsaoFim_tipo=cd["previsaoFim_tipo"],
                previsao_fim=cd.get("previsao_fim"),
                paciente_id=cd["paciente"].pk,
                checkIn=cd.get("checkIn"),
                acompanhante_id=cd["acompanhante"].pk if cd.get("acompanhante") else None,
                tipoVinculo_acompanhante=cd.get("tipoVinculo_acompanhante", ""),
                descricao_vinculo=cd.get("descricao_vinculo", ""),
                solicitante_id=cd["solicitante"].pk if cd.get("solicitante") else None,
                descHospedagem=cd.get("descHospedagem", ""),
                quarto_id=cd["quarto"].pk if cd.get("quarto") else None,
                inicio_alocacao=cd["data_inicio"]
            )
            messages.success(request, f"Apoio #{apoio.pk} registrado com sucesso.")
            return redirect("apoio:detalhe", pk=apoio.pk)

        #except ApoioComHospedagemNecessario as exc:
            # alt02: redireciona para UC22
           # messages.info(
             #   request,
             #   "O apoio possui duração superior a um dia. "
              #  "Prossiga com o cadastro de hospedagem.",
            #)
            # Preserva os dados no formulário e redireciona para o fluxo de hospedagem
            #return redirect(
             #   f"/apoio/iniciar-com-hospedagem/?data_inicio={exc.data_inicio}"
              #  f"&previsao_fim={exc.previsao_fim}"
            #)

        except ValidationError as exc:
            for msg in exc.messages:
                messages.error(request, msg)

    return render(request, "apoio/iniciar_apoio.html", {
        "form": form,
        "quarto_selecionado": quarto_obj,
        "precisa_hospedagem": precisa_hospedagem})

def detalhe_apoio_view(request, pk):
    apoio = get_object_or_404(Apoio, pk=pk)
    return render(request, "apoio/detalhe_apoio.html", {"apoio": apoio, "hospedagem": getattr(apoio, "hospedagem", None)})

def checkin_apoio_view(request, pk):
    apoio = get_object_or_404(Apoio, pk=pk, status=True)
    try:
        checkIn_apoio(apoio.pk)
        messages.success(request, "Check-in do paciente registrado")
    except ValidationError as exc:
        for msg in exc.messages:
            messages.error(request, msg)
    return redirect("apoio:detalhe", pk=pk)

def checkout_apoio_view(request, pk):
    apoio = get_object_or_404(Apoio, pk=pk, status=True)
    try:
        checkOut_apoio(apoio.pk)
        messages.success(request, "Check-out do paciente registrado")
    except ValidationError as exc:
        for msg in exc.messages:
            messages.error(request, msg)
    return redirect("apoio:detalhe", pk=pk)

def adicionar_acompanhante_view(request, pk):
    apoio = get_object_or_404(Apoio, pk=pk, status=True)
    form = AdicionarAcompanhante(request.POST or None)

    if request.method == "POST" and form.is_valid():
        cd = form.cleaned_data
        acompanhante = cd.get("acompanhante")
        if not acompanhante:
            messages.error(request, "Selecione um acompanhante")
            return render(request, "apoio/adicionar_acompanhante.html", {
                "form": form,
                "apoio":apoio
            })
        try:
            vincular_acompanhante(
                apoio=apoio,
                acompanhante_id=acompanhante.pk,
                tipoVinculo_acompanhante=cd.get("tipoVinculo_acompanhante", ""),
                descricao_vinculo=cd.get("descricao_vinculo", ""),
            )
            messages.success(request, "Acompanhante adicionado com sucesso.")
            return redirect("apoio:detalhe", pk=apoio.pk)
        except ValidationError as exc:
            for msg in exc.messages:
                messages.error(request, msg)

    return render(request, "apoio/adicionar_acompanhante.html", {
        "form": form,
        "apoio": apoio
    })

def checkout_acompanhante_view(request, pk):
    apoio = get_object_or_404(Apoio, pk=pk, status=True)
    try:
        acompanhante = apoio.acompanhante_atual
        if not acompanhante:
            raise ValidationError("Acompanhante não encontrado")
        checkout_acompanhante(acompanhante.pk)
        messages.success(request, "Checkout de acompanhante realizado")
    except ValidationError as exc:
        for msg in exc.messages:
            messages.error(request, msg)

    return redirect("apoio:detalhe", pk=pk)

def selecionar_quarto_view(request):
    quartos = Quarto.objects.filter(status=True)

    return render(request, "apoio/selecionar_quarto.html", {
        "quartos": quartos
    })

def editar_apoio_view(request, pk):
    apoio = get_object_or_404(Apoio, pk=pk)

    quarto_id = request.GET.get("quarto_id")
    quarto_obj = None

    if quarto_id:
        quarto_obj = Quarto.objects.filter(pk=quarto_id).first()

    if not quarto_obj:
        hospedagem = getattr(apoio, "hospedagem", None)
        if hospedagem:
            atual = hospedagem.hospedagem_alocacao.filter(
                fimLocacao__isnull=True
            ).first()
            if atual:
                quarto_obj = atual.quarto

    initial = {
        "motivo_apoio": apoio.motivo,
        "previsaoFim_tipo": apoio.previsaoFim_tipo,
        "previsao_fim": apoio.previsaoFim,
        "solicitante": apoio.solicitante,
        "descHospedagem": getattr(apoio, "hospedagem", None) and apoio.hospedagem.observacao,
        "quarto": quarto_obj,
    }

    form = EditarApoioForm(request.POST or None, initial=initial)

    if request.method == "POST" and form.is_valid():
        cd = form.cleaned_data

        try:
            editar_apoio(
                apoio_id=apoio.pk,
                motivo_apoio=cd["motivo_apoio"],
                previsaoFim_tipo=cd["previsaoFim_tipo"],
                previsao_fim=cd.get("previsao_fim"),
                solicitante_id=cd["solicitante"].pk if cd.get("solicitante") else None,
                descHospedagem=cd.get("descHospedagem"),
                quarto_id=cd["quarto"].pk if cd.get("quarto") else None,
                inicio_alocacao=cd["inicio_alocacao"]
            )

            messages.success(request, "Apoio atualizado com sucesso")
            return redirect("apoio:detalhe", pk=apoio.pk)

        except ValidationError as exc:
            for msg in exc.messages:
                messages.error(request, msg)

    return render(request, "apoio/editar_apoio.html", {
        "form": form,
        "apoio": apoio,
        "quarto_selecionado": quarto_obj
    })

def listar_apoios_view(request):

    apoios = Apoio.objects.all().order_by("-dataInicio")

    return render(
        request,
        "apoio/listar_apoios.html",
        {
            "apoios": apoios
        }
    )