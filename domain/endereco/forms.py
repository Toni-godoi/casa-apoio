from django import forms
from django.utils import timezone
from datetime import date, time, datetime, timedelta
from django.core.exceptions import ValidationError
from domain.endereco.models import Endereco, Pais, Estado, Cidade, Bairro
from domain.endereco.services import buscar_endereco_cep

class CadastrarEditarBairro(forms.Form):

    bairro = forms.CharField(
            max_length=100,
            widget=forms.TextInput(attrs={"class": "form-control"})
        )
    
    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

class CadastrarCidade(forms.Form):

    cidade = forms.CharField(
            max_length=100,
            widget=forms.TextInput(attrs={"class": "form-control"})
        )

    estado = forms.ModelChoiceField(
            queryset=Estado.objects.all(),
            empty_label="Selecione",
            label="Estado",
            widget=forms.Select(
                attrs={"id": "id_estado", 
                        "class": "form-select",
                        "placeholder": "Selecione",}),
            )
    
    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

class EndercoForm(forms.Form):

    pais = forms.ModelChoiceField(
        queryset=Pais.objects.all(),
        empty_label="Selecione",
        label="Pais",
        widget=forms.Select(
            attrs={"id": "id_pais", 
                   "class": "form-select"}),
    )

    estado = forms.ModelChoiceField(
            queryset=Estado.objects.all(),
            empty_label="Selecione",
            required=False,
            label="Estado",
            widget=forms.Select(
                attrs={"id": "id_estado", 
                       "class": "form-select",
                       "placeholder": "Selecione",}),
        )

    cidade = forms.ModelChoiceField(
            queryset=Cidade.objects.all(),
            empty_label="Selecione",
            required=False,
            label="Cidade",
            widget=forms.Select(
                attrs={
                "id": "id_cidade",
                "class": "form-select",}),
        )

    bairro = forms.ModelChoiceField(
            queryset=Bairro.objects.all(),
            empty_label="Selecione",
            required=False,
            label="Bairro",
            widget=forms.Select(
                attrs={
                "id": "id_bairro",
                "class": "form-select",}),
        )   

    cep = forms.CharField(
            max_length=9,
            required=False,
            label="CEP",
            widget=forms.TextInput(
                attrs={
                    "class": "form-control",
                    "id": "id_cep",
                    "placeholder": "00000-000",
                    "maxlength": "9",
                }
            ),
        )
    
    logradouro = forms.CharField(
        max_length=255,
        required=False,
        label="Logradouro",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "id": "id_logradouro"}),
    )

    numero = forms.CharField(
        max_length=20,
        required=False,
        label="Número",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "id": "id_numero"}),
    )

    complemento = forms.CharField(
        max_length=100,
        required=False,
        label="Complemento",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "id": "id_complemento"}),
    )

    descricao = forms.CharField(
        max_length=100,
        required=False,
        label="Complemento",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "id": "id_descricao"}),
    )

    def clean(self):
        cleaned_data = super().clean()
    
        return cleaned_data