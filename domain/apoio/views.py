from django.contrib import messages
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from domain.apoio.forms import IniciarApoioForm, AdicionarAcompanhante, EditarApoioForm
from domain.apoio.models import Apoio
from domain.quarto.models import Quarto
from domain.pessoa.models import Pessoa
from domain.solicitacao.models import SolicitantePessoa
from domain.apoio.services import iniciar_apoio, editar_apoio, vincular_acompanhante, checkout_acompanhante, checkIn_apoio, checkOut_apoio

# Create your views here. #Entoni
@login_required
def iniciar_apoio_view(request):

    quarto_id = request.GET.get("quarto_id")
    quarto_obj = None
    pacientes = Pessoa.objects.all()
    acompanhantes = Pessoa.objects.all()
    solicitantes = SolicitantePessoa.objects.all()

    form = IniciarApoioForm(request.POST or None)
    form.fields["paciente"].choices = [("", "Digite um nome")]+[(p.id, p.nome_pessoa)for p in pacientes]
    form.fields["solicitante"].choices = [("", "Digite um nome")]+[(p.id, p.pessoa)for p in solicitantes]
    form.fields["acompanhante"].choices = [("", "Digite um nome")]+[(p.id, p.nome_pessoa)for p in acompanhantes]

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
                paciente_id=cd["paciente"],
                checkIn=cd.get("checkIn"),
                acompanhante_id=cd["acompanhante"] if cd.get("acompanhante") else None,
                tipoVinculo_acompanhante=cd.get("tipoVinculo_acompanhante", ""),
                descricao_vinculo=cd.get("descricao_vinculo", ""),
                solicitante_id=cd["solicitante"] if cd.get("solicitante") else None,
                descHospedagem=cd.get("descHospedagem", ""),
                quarto_id=cd["quarto"].pk if cd.get("quarto") else None,
                inicio_alocacao=cd["data_inicio"]
            )
            return redirect("apoio:detalhe", pk=apoio.pk)
        
        except ValidationError as exc:
            for msg in exc.messages:
                messages.error(request, msg)

    return render(request, "apoio/iniciar_apoio.html", {
        "form":form,
        "quarto_selecionado": quarto_obj,
        "precisa_hospedagem": precisa_hospedagem})

@login_required
def detalhe_apoio_view(request, pk):
    apoio = get_object_or_404(Apoio, pk=pk)
    return render(request, "apoio/detalhe_apoio.html", {"apoio": apoio, "hospedagem": getattr(apoio, "hospedagem", None)})

@login_required
def checkin_apoio_view(request, pk):
    apoio = get_object_or_404(Apoio, pk=pk, status=True)
    try:
        checkIn_apoio(apoio.pk)
        messages.success(request, "Check-in do paciente registrado")
    except ValidationError as exc:
        for msg in exc.messages:
            messages.error(request, msg)
    return redirect("apoio:detalhe", pk=pk)

@login_required
def checkout_apoio_view(request, pk):
    apoio = get_object_or_404(Apoio, pk=pk, status=True)
    try:
        checkOut_apoio(apoio.pk)
        messages.success(request, "Check-out do paciente registrado")
    except ValidationError as exc:
        for msg in exc.messages:
            messages.error(request, msg)
    return redirect("apoio:detalhe", pk=pk)

@login_required
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

@login_required
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

@login_required
def selecionar_quarto_view(request):
    quartos = Quarto.objects.filter(status=True)

    return render(request, "apoio/selecionar_quarto.html", {
        "quartos": quartos
    })

@login_required
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
        "solicitante": apoio.solicitante.pk if apoio.solicitante else None,
        "descHospedagem": getattr(apoio, "hospedagem", None) and apoio.hospedagem.observacao,
        "quarto": quarto_obj,
    }

    solicitantes = SolicitantePessoa.objects.all()

    form = EditarApoioForm(request.POST or None, initial=initial)

    form.fields["solicitante"].choices = [("", "Digite um nome")]+[(p.id, p.pessoa)for p in solicitantes]

    if request.method == "POST" and form.is_valid():
        cd = form.cleaned_data

        try:
            editar_apoio(
                apoio_id=apoio.pk,
                motivo_apoio=cd["motivo_apoio"],
                previsaoFim_tipo=cd["previsaoFim_tipo"],
                previsao_fim=cd.get("previsao_fim"),
                solicitante_id=cd["solicitante"] if cd.get("solicitante") else None,
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

@login_required
def listar_apoios_view(request):

    apoios = Apoio.objects.filter(
        status=True).order_by("-dataInicio")
    return render(request,"apoio/listar_apoios.html",{"apoios": apoios})

@login_required
def consultar_apoios_view(request):

    paciente = request.GET.get("paciente")
    solicitante = request.GET.get("solicitante")
    data_inicio = request.GET.get("data_inicio")
    data_fim = request.GET.get("data_fim")
    previsaoFim_tipo = request.GET.get("previsaoFim_tipo")
    checkIn_inicio = request.GET.get("data_inicio_checkIn")
    checkIn_fim = request.GET.get("data_fim_checkIn")
    checkOut_inicio = request.GET.get("data_inicio_checkOut")
    checkOut_fim = request.GET.get("data_fim_checkOut")

    apoios = Apoio.objects.none()
    if any([paciente, solicitante, data_inicio, data_fim, previsaoFim_tipo, checkIn_inicio, checkIn_fim, checkOut_inicio, checkOut_fim]):
        
        apoios = Apoio.objects.all()
        if paciente:
            apoios = apoios.filter(paciente__nome_pessoa__icontains=paciente)
        if solicitante:
            apoios = apoios.filter(solicitante__pessoa__nome_pessoa__icontains=solicitante)
        if previsaoFim_tipo:
            apoios = apoios.filter(previsaoFim_tipo__icontains=previsaoFim_tipo)
        if checkIn_inicio and checkIn_fim:
            checkIn_inicio_dt = datetime.strptime(checkIn_inicio, "%Y-%m-%d").date()
            checkIn_fim_dt = datetime.strptime(checkIn_fim, "%Y-%m-%d").date()
            diferenca = (checkIn_fim_dt - checkIn_inicio_dt).days
            try:
                if diferenca>90:
                    raise ValidationError("Escolha um periodo menor que 90 dias")
                if diferenca <0:
                    raise ValidationError("Periodo de check-in invalido")
                apoios = apoios.filter(checkIn__range=[checkIn_inicio,checkIn_fim])
            except ValidationError as exc:
                messages.error(request, exc.messages[0])

        if checkOut_inicio and checkOut_fim:
            checkOut_inicio_dt = datetime.strptime(checkOut_inicio, "%Y-%m-%d").date()
            checkOut_fim_dt = datetime.strptime(checkOut_fim, "%Y-%m-%d").date()
            diferenca = (checkOut_fim_dt - checkOut_inicio_dt).days
            try:
                if diferenca>90:
                    raise ValidationError("Escolha um periodo menor que 90 dias")
                if diferenca <0:
                    raise ValidationError("Periodo de check-out invalido")
                apoios = apoios.filter(checkOut__range=[checkOut_inicio,checkOut_fim])
            except ValidationError as exc:
                messages.error(request, exc.messages[0])

        if data_inicio and data_fim:
            data_inicio_dt = datetime.strptime(data_inicio, "%Y-%m-%d").date()
            data_fim_dt = datetime.strptime(data_fim, "%Y-%m-%d").date()
            diferenca = (data_fim_dt - data_inicio_dt).days
            try:
                if diferenca>90:
                    raise ValidationError("Escolha um periodo menor que 90 dias")
                if diferenca <0:
                    raise ValidationError("Periodo de cadastro invalido")
                apoios = apoios.filter(dataInicio__range=[data_inicio,data_fim])
            except ValidationError as exc:
                messages.error(request, exc.messages[0])

    return render(request,"apoio/consultar_apoios.html",{"apoios": apoios})