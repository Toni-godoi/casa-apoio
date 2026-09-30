from django.shortcuts import render
from django.contrib import messages
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from domain.pessoa.forms import CadastrarEditarPessoaForm
from domain.pessoa.utils import calcular_idade
from domain.pessoa.models import Pessoa, FotoPerfilPessoa, PessoaEditada, DeficienciaPessoa, Deficiencia
from domain.pessoa.services import cadastrar_pessoa, editar_pessoa
from domain.endereco.forms import EndercoForm
from domain.endereco.models import Pais, Estado, Cidade, Bairro, Endereco
from domain.endereco.services import cadastrar_end_pessoa, editar_end_pessoa
from domain.apoio.models import Apoio

# Create your views here.
@login_required
def cadastrar_pessoa_view(request):

    form = CadastrarEditarPessoaForm(request.POST or None, request.FILES or None)
    form_end = EndercoForm(request.POST or None)
    idade = None
    
    if request.method == "POST" and form.is_valid() and form_end.is_valid():

        data_nascimento = form.cleaned_data['dataNasc_pessoa']
        idade = calcular_idade(data_nascimento)
        foto_pessoa = form.cleaned_data.get("foto")
        
        cd = form.cleaned_data
        cd_end = form_end.cleaned_data

        valor_bairro = cd_end['bairro']
        if valor_bairro.isdigit():
            int_bairro = int(valor_bairro)
            bairro = Bairro.objects.get(pk=int_bairro)
            nome_bairro = bairro.nome_bairro
        else:
            nome_bairro = valor_bairro

        valor_cidade = cd_end['cidade']
        if valor_cidade.isdigit():
            int_cidade = int(valor_cidade)
            cidade = Cidade.objects.get(pk=int_cidade)
            nome_cidade = cidade.nome_cidade
        else:
            nome_cidade = valor_cidade

        valor_estado = cd_end['estado']
        if valor_estado.isdigit():
            int_estado = int(valor_estado)
            estado = Estado.objects.get(pk=int_estado)
            nome_estado = estado.nome_estado
        else:
            nome_estado = valor_estado

        try:
            endereco = cadastrar_end_pessoa(
                pais = cd_end['pais'].pk,
                cep = cd_end['cep'],
                estado = nome_estado,
                uf_estado=cd_end["uf_estado"],
                cidade = nome_cidade,
                bairro = nome_bairro,
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
                deficiencia=cd['deficiencia'],
                tipos_deficiencias=cd['tipos_deficiencias'],
                endereco_pessoa = endereco
            )
            return redirect ("pessoa:dados_pessoa", pessoa.pk)

        except ValidationError as e:
            form.add_error(None, e.message)
        #except ValidationError as exc:
            #for msg in exc.messages:
               # messages.error(request, msg)
    paises = list(Pais.objects.values("id", "nome_pais"))
    estados = list(Estado.objects.values("id", "pais_id", "nome_estado", "uf_estado"))
    cidades = list(Cidade.objects.values("id", "estado_id", "nome_cidade"))
    bairros = list(Bairro.objects.values("id", "cidade_id", "nome_bairro"))

    return render(request, "pessoa/cadastrar_pessoa.html", {
        "form": form,
        "form_end": form_end,
        "idade": idade,
        "paises": paises,
        "estados": estados,
        "cidades": cidades,
        "bairros": bairros})

@login_required
def editar_pessoa_view(request, pk):
    pessoa = get_object_or_404(Pessoa, pk=pk)

    deficiencias = DeficienciaPessoa.objects.filter(pessoa = pessoa)
    tipos_selecionados = deficiencias.values_list("deficiencia_id", flat=True)
    initial = {
        'nome_pessoa': pessoa.nome_pessoa,
        'cpf_pessoa':pessoa.cpf_pessoa,
        'sexo_pessoa':pessoa.sexo_pessoa,
        'dataNasc_pessoa':pessoa.dataNasc_pessoa.strftime("%Y-%m-%d"),
        'nacionalidade_pessoa':pessoa.nacionalidade_pessoa,
        'telefone_pessoa':pessoa.telefone_pessoa,
        'email_pessoa':pessoa.email_pessoa,
        'descricao_pessoa':pessoa.descricao_pessoa,
        'deficiencia':pessoa.deficiencia,
        'tipos_deficiencias':tipos_selecionados
    }
    
    endereco = pessoa.endereco
    bairro = endereco.bairro
    cidade = bairro.cidade
    estado = cidade.estado
    pais = estado.pais

    initial_end = {
        'pais': pais.pk,
        'cep': endereco.cep,
        'estado': estado.nome_estado,
        'uf_estado': estado.uf_estado,
        'cidade': cidade.nome_cidade,
        'bairro': bairro.nome_bairro,
        'logradouro': endereco.logradouro,
        'numero': endereco.numero,
        'complemento': endereco.complemento,
        'descricao': endereco.descricao,
    }

    form = CadastrarEditarPessoaForm(request.POST or None, initial=initial)
    form_end = EndercoForm(request.POST or None, initial=initial_end)

    estados = list(
        Estado.objects
        .filter(pais=pais)
        .order_by("nome_estado")
        .values(
            "id",
            "pais_id",
            "nome_estado",
            "uf_estado"
        )
    )

    form_end.fields["estado"].widget.choices = [
        ("", "Selecione")
    ] + [
        (
            estado_item["nome_estado"],
            estado_item["nome_estado"]
        )
        for estado_item in estados
    ]

    cidades = list(
        Cidade.objects
        .filter(estado=estado)
        .order_by("nome_cidade")
        .values(
            "id",
            "estado_id",
            "nome_cidade"
        )
    )

    form_end.fields["cidade"].widget.choices = [
        ("", "Selecione")
    ] + [
        (
            cidade_item["nome_cidade"],
            cidade_item["nome_cidade"]
        )
        for cidade_item in cidades
    ]

    bairros = list(
        Bairro.objects
        .filter(cidade=cidade)
        .order_by("nome_bairro")
        .values(
            "id",
            "cidade_id",
            "nome_bairro"
        )
    )

    form_end.fields["bairro"].widget.choices = [
        ("", "Selecione")
    ] + [
        (
            bairro_item["nome_bairro"],
            bairro_item["nome_bairro"]
        )
        for bairro_item in bairros
    ]

    if request.method == "POST" and form.is_valid() and form_end.is_valid():
        cd = form.cleaned_data
        cd_end = form_end.cleaned_data

        try:
            endereco = editar_end_pessoa(
                ed_endereco_id=pessoa.endereco.pk,
                ed_pais = cd_end['pais'].pk,
                ed_cep = cd_end['cep'],
                ed_estado = cd_end['estado'],
                ed_uf_estado=cd_end["uf_estado"],
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
                ed_deficiencia=cd['deficiencia'],
                ed_tipos_deficiencias=cd['tipos_deficiencias'],
                ed_descricao_pessoa=cd['descricao_pessoa']
            )
            return redirect ("pessoa:dados_pessoa", pessoa.pk)

        except ValidationError as e:
            form.add_error(None, e.message)

    paises = list(
        Pais.objects.values(
            "id",
            "nome_pais"
        )
    )

    estados_js = list(
        Estado.objects.values(
            "id",
            "pais_id",
            "nome_estado",
            "uf_estado"
        )
    )

    cidades_js = list(
        Cidade.objects.values(
            "id",
            "estado_id",
            "nome_cidade"
        )
    )

    bairros_js = list(
        Bairro.objects.values(
            "id",
            "cidade_id",
            "nome_bairro"
        )
    )

    return render(request, "pessoa/editar_pessoa.html", {
        "form": form,
        "form_end": form_end, 
        "pessoa":pessoa,
        "paises": paises,
        "estados": estados_js,
        "cidades": cidades_js,
        "bairros": bairros_js,
        "endereco_inicial": initial_end,})

@login_required
def dados_pessoa_view(request, pk):
    pessoa = get_object_or_404(Pessoa, pk=pk)
    deficiencias = DeficienciaPessoa.objects.filter(pessoa = pessoa)

    apoios=[]
    for apoio in pessoa.pacientes.all():
        apoios.append({
            "apoio": apoio,
            "participacao": "Paciente",
            "checkin": apoio.checkIn,
            "checkout": apoio.checkOut})
        
    for acomp in pessoa.vinculos_acompanhantes.all():
        apoios.append({
            "apoio": acomp.apoio,
            "participacao": "Acompanhante",
            "checkin": acomp.checkIn,
            "checkout": acomp.checkOut,})

    apoios.sort(
        key=lambda x: x["apoio"].id,
        reverse=True)

    return render(request, "pessoa/dados_pessoa.html", {
        "pessoa": pessoa,
        "deficiencias": deficiencias,
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



