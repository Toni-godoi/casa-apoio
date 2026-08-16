from django import forms
from django.utils import timezone
from datetime import date, time, datetime, timedelta
from domain.quarto.models import Quarto

class QuartoForm(forms.Form):

    identificacao = forms.CharField(
        max_length=20,
        label="Identificação",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    descricao = forms.CharField(
            label="Descrição",
            widget=forms.TextInput(attrs={"class": "form-control"})
        )

    quantidadeVagas = forms.IntegerField(
        label="Quantidade de vagas",
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )

    def clean(self):
        return super().clean()

