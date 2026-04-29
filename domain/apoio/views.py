from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError

from domain.apoio.forms import IniciarApoioForm, AdicionarAcompanhante
from domain.apoio.models import Apoio
from domain.apoio.services import iniciar_apoio, vincular_acompanhante, checkout_acompanhante, checkIn_apoio, checkOut_apoio

# Create your views here.
def iniciar_apoio_view(request):
    
    form = IniciarApoioForm(request.POST or None)

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
                obs_hospedagem=cd.get("obs_hospedagem", ""),
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

    return render(request, "apoio/iniciar_apoio.html", {"form": form})

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