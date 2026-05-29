from django import forms
from django.utils import timezone
from datetime import date, time, datetime, timedelta
from domain.solicitacao.models import FuncaoSolicitantePessoa, SolicitantePessoa

class CadastrarFuncaoForm(forms.Form):

    funcao = forms.CharField(
        max_length=20,
        label="Nome da função",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    descricao = forms.CharField(
        max_length=50,
        required=False,
        label="Adicione uma descrição",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    def clean(self):
        return super().clean()


class CadastrarSolicitantePessoaForm(forms.Form):

    pessoa = forms.ChoiceField(
        choices=[],
        widget=forms.Select()
        )

    funcao = forms.ChoiceField(
        choices=[],
        widget=forms.Select(
        attrs={"class": "form-select"})
        )

    descricao = forms.CharField(
        max_length=20,
        required=False,
        label="Adicione uma descrição",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    def clean(self):
        return super().clean()