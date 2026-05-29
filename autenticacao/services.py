from typing import Optional
from django.db import transaction
from django.utils import timezone
from validate_docbr import CPF
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from datetime import date, time, datetime, timedelta
from django.db.models import Q

from autenticacao.models import GerenciarUsuario, Usuario

def autenticar_usuario(credencial, senha):
    try:
        usuario = Usuario.objects.get(
            Q(email=credencial) | Q(loginUsuario=credencial))
    except Usuario.DoesNotExist:
        return None
    
    if usuario.check_password(senha):
        return usuario
    
    return None
