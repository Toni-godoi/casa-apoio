from django import forms
from django.utils import timezone
from datetime import date, time, datetime, timedelta

from autenticacao.models import GerenciarUsuario

class LoginForm(forms.Form):
    credencial = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'email ou usuário', "class": "form-control"}))

    senha = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder':'Digite a senha', 'class':'form-control'}
    ))

    