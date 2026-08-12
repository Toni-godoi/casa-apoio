from django import forms
from django.utils import timezone
from datetime import date, time, datetime, timedelta
from domain.pessoa.models import Pessoa
from domain.apoio.models import Apoio, Acompanhante
from domain.quarto.models import Quarto
from domain.solicitacao.models import SolicitantePessoa

class IniciarApoioForm(forms.Form):

    #casa_apoio
    motivo_apoio = forms.CharField(
        max_length=20,
        label="Adicione uma descrição",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    data_inicio = forms.DateField(
        initial=timezone.localdate,
        label="Data de início do apoio",
        disabled=True
    )

    previsaoFim_tipo = forms.ChoiceField(
        choices=[('HOJE', 'Hoje'),('DATA','Data'),('INDETERMINADO','Indeterminado')],
        required=False,
        label = "Previsão de encerramento",
        widget=forms.RadioSelect
    )

    previsao_fim = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type":"date", "class": "form-control"}),
        label="Data de Nascimento"
    )

    paciente = forms.ChoiceField(
        choices=[],
        widget=forms.Select()
    )

    checkIn = forms.BooleanField(
    required=False,
    label="Selecione se o paciente for fazer check-in agora",
    widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )

    acompanhante = forms.ChoiceField(
        required=False,
        choices=[],
        widget=forms.Select()
    )

    tipoVinculo_acompanhante = forms.ChoiceField(
        choices=[('PAI_MAE', 'Pai ou Mãe'),('CONJUGUE', 'Conjugue'), ('OUTROS', 'Outros')],
        label = "Previsão de encerramento",
        required=False,
        widget=forms.RadioSelect
    )

    descricao_vinculo = forms.CharField(
        max_length=300,
        required=False,
        label="Descrição do vínculo com paciente",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    solicitante = forms.ChoiceField(
        required=False,
        choices=[],
        widget=forms.Select()
    )

    descHospedagem = forms.CharField(
        max_length=500,
        required=False,
        label="Descrição do vínculo com paciente",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    quarto = forms.ModelChoiceField(
        queryset=Quarto.objects.filter(status=True),
        required=False,
        label="Quarto",
        widget=forms.HiddenInput()
    )

    inicio_alocacao = forms.DateField(
        initial=timezone.localdate,
        label="Data de início da alocação do quarto",
        disabled=True
    )

    def clean(self):
        cleaned = super().clean()
        data_inicio = cleaned.get("data_inicio")
        previsao_fim = cleaned.get("previsao_fim")
        
        data_inicio_mais = data_inicio + timedelta(days=1)

        if data_inicio and previsao_fim and previsao_fim < data_inicio_mais:
            self.add_error(
                "previsao_fim", "A previsão de fim precisa de uma data após a data de inicio.",)

        #define tipo de fim como HOJE ao criar apoio, 
        #para não ser preciso selecionar quarto na criação
        #Quarto so deve ser selecionado na edição do apoio
        fim_tipo = cleaned.get("previsaoFim_tipo")
        if not fim_tipo:
            cleaned["previsaoFim_tipo"] = "HOJE"
        ####
        return cleaned

class AdicionarAcompanhante(forms.Form):
    
    acompanhante = forms.ModelChoiceField(
        queryset=Pessoa.objects.all(),
        required=False,
        label="Acompanhante",
        help_text="Selecione"
    )

    tipoVinculo_acompanhante = forms.ChoiceField(
        choices=[("","---------")] + Acompanhante.VINCULO_CHOICES,
        required=False,
        label="Vinculo do acompanhante com paciente"
    )

    descricao_vinculo = forms.CharField(
        max_length=300,
        required=False,
        label="Descrição de vinculo",
        help_text="Obrigatório para outros tipos de vinculo"
    )

class EditarApoioForm(forms.Form):

    motivo_apoio = forms.CharField(
        max_length=20,
        label="Adicione uma descrição",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    previsaoFim_tipo = forms.ChoiceField(
        choices=[('HOJE', 'Hoje'),('DATA','Data'),('INDETERMINADO','Indeterminado')],
        label = "Previsão de encerramento",
        widget=forms.RadioSelect
    )

    previsao_fim = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type":"date", "class": "form-control"}),
        label="Data de Nascimento"
    )

    solicitante = forms.ChoiceField(
        required=False,
        choices=[],
        widget=forms.Select()
    )

    descHospedagem = forms.CharField(
        max_length=500,
        required=False,
        label="Descrição do vínculo com paciente",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    quarto = forms.ModelChoiceField(
        queryset=Quarto.objects.filter(status=True),
        required=False,
        label="Quarto",
        widget=forms.HiddenInput()
    )

    inicio_alocacao = forms.DateField(
        initial=timezone.localdate,
        label="Data de início para hospedagem de quarto",
        disabled=True
    )