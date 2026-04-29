from django import forms
from django.utils import timezone
from datetime import date, time, datetime, timedelta
from domain.pessoa.models import Pessoa
from domain.apoio.models import Apoio, Acompanhante
from domain.quarto.models import Quarto

class IniciarApoioForm(forms.Form):

    #casa_apoio
    motivo_apoio = forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={"rows": 3}),
        label="Motivo do Apoio",
    )

    data_inicio = forms.DateField(
        initial=timezone.localdate,
        label="Data de início do apoio",
        disabled=True
    )

    previsaoFim_tipo = forms.ChoiceField(
        choices=[("","----------------")] + Apoio.DATAFIM_CHOICES,
        label="Previsão de encerramento do apoio"
    )

    previsao_fim = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type":"date"}),
        label="Data prevista para fim do apoio",
        help_text="Obrigatório quando existe uma data previsa diferente do mesmo dia"
    )

    paciente = forms.ModelChoiceField(
        queryset=Pessoa.objects.all(),
        label="Paciente",
        help_text="Selecione"
    )

    checkIn = forms.BooleanField(
    required=False,
    label="Selecione se o paciente for fazer check-in agora",
    )

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
        help_text="Obrigatório para vinculos de tipo 'Outros'"
    )

    solicitante = forms.ModelChoiceField(
        queryset=Pessoa.objects.filter(aptaSolicitante_pessoa=True),
        required=False,
        label="Solicitante do apoio",
        help_text="Obrigatório se o apoio precisar de hospedagem"
    )

    obs_hospedagem = forms.CharField(
        max_length=500,
        required=False,
        label="Observações para hopedagem",
        help_text="Apenas em caso de hospedagem"
    )

    quarto = forms.ModelChoiceField(
        queryset=Quarto.objects.filter(status=True),
        required=False,
        label="Quarto",
        help_text="Obrigatório se tempo do apoio for maior que hoje"
    )

    inicio_alocacao = forms.DateField(
        initial=timezone.localdate,
        label="Data de início hospedagem",
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