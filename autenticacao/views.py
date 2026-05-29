from django.shortcuts import render
from django.contrib import messages
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError
from django.contrib.auth import login
from django.contrib.auth import logout

from autenticacao.services import autenticar_usuario
from autenticacao.forms import LoginForm
from projetoApoio import settings
# Create your views here.

def login_view(request):

    if settings.TIPO_AUTENTICACAO == "OIDC":
        # Redireciona para o Authentik
        #pass
        return redirect("oidc_authentication_init")

    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            usuario = autenticar_usuario(
                cd['credencial'],
                cd['senha']
            )
        if usuario:
            login(request, usuario)
            return redirect('home')
        
        messages.error(request,'login ou senha inválidos')
    
    return render(request, "autenticacao/login.html", {'form':form})

def logout_view(request):
    logout(request)
    return redirect("autenticacao:login")
