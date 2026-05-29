from django import forms
from django.utils import timezone
from datetime import date, time, datetime, timedelta
from domain.pessoa.models import Pessoa, PessoaEditada

class CadastrarEditarPessoaForm(forms.Form):

    nome_pessoa = forms.CharField(
        max_length=30,
        label="Nome completo",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    cpf_pessoa = forms.CharField(
        max_length=14,
        label="CPF",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    sexo_pessoa = forms.ChoiceField(
        choices=[('F','Feminino'),('M','Masculino')],
        label = "Sexo",
        widget=forms.RadioSelect
    )

    dataNasc_pessoa = forms.DateField(
        widget=forms.DateInput(attrs={"type":"date", "class": "form-control"}),
        label="Data de Nascimento"
    )

    nacionalidade_pessoa = forms.ChoiceField(
        choices=[("","selecionar")] + Pessoa.PAIS_CHOICES,
        label="Nacionalidade",
        widget=forms.Select(attrs={"class": "form-select"})
    )

    telefone_pessoa = forms.CharField(
        max_length=16,
        label="Telefone de contato",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    email_pessoa = forms.EmailField(
        required=False,
        max_length=50,
        widget=forms.EmailInput(attrs={"class": "form-control"})
    )

    descricao_pessoa = forms.CharField(
        max_length=50,
        required=False,
        label="Outras Informações",
        widget=forms.Textarea(attrs={"class": "form-control","rows": 2})
    )

    #endereco

    def clean(self):
        return super().clean()
