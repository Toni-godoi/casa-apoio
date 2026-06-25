from django import forms
from django.utils import timezone
from datetime import date, time, datetime, timedelta
from django.core.exceptions import ValidationError
from domain.endereco.models import Endereco
from domain.endereco.services import buscar_endereco_cep

CAMPOS_OBRIGATORIOS_BRASIL = ["cep", "estado", "cidade", "bairro", "logradouro"]
SIGLAS_BRASIL = {sigla for sigla, _ in Endereco.ESTADO_CHOICES if sigla}

class BrasilEndercoForm(forms.Form):

    pais = forms.ChoiceField(
        choices=[("","selecionar")] + Endereco.PAIS_CHOICES,
        initial="BR",
        label="Pais",
        widget=forms.Select(
            attrs={"class": "form-select"}),
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

    estado = forms.ChoiceField(
        choices=[("","selecionar")] + Endereco.ESTADO_CHOICES,
        initial="",
        required=False,
        label="Estado",
        widget=forms.Select(
            attrs={"class": "form-select"}),
    )

    cidade = forms.CharField(
        max_length=100,
        required=False,
        label="Cidade",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "id": "id_cidade"}),
    )

    bairro = forms.CharField(
        max_length=100,
        required=False,
        label="Bairro",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "id": "id_bairro"}),
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

    class Meta:
        model = Endereco
        fields = [
            "pais",
            "cep",
            "estado",
            "cidade",
            "bairro",
            "logradouro",
            "numero",
            "complemento",
            "descricao",
        ]
 
    def clean(self):
        cleaned_data = super().clean()
        pais = cleaned_data.get("pais")
        descricao = cleaned_data.get("descricao")

        if pais == "BR":
            # Obrigatoriedade dos campos brasileiros
            for campo in CAMPOS_OBRIGATORIOS_BRASIL:
                valor = cleaned_data.get(campo)
                if not valor or not valor.strip():
                    label = self.fields[campo].label
                    self.add_error(
                        campo,
                        f"{label} é obrigatório para endereços no Brasil.",
                    )
 
            # Valida que a sigla de estado é uma UF válida
            estado = cleaned_data.get("estado", "")
            if estado and estado.upper() not in SIGLAS_BRASIL:
                self.add_error(
                    "estado",
                    "Selecione um estado válido.",
                )
        if pais != 'BR' and not descricao:
            #self.add_error("Descreva o endereço estrangeiro")
            raise ValidationError("Descreva o endereço estrangeiro")

        return cleaned_data