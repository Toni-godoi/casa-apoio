from django.shortcuts import render
from django.contrib import messages
from datetime import datetime
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from domain.solicitante.models import SetorUnidadeSolicitante, UnidadeSolicitante

# Create your views here.
def listar_origens_view(request):
    origens = UnidadeSolicitante.objects.all()

    return render(request,"solicitacao/listar_origens.html",{"origens": origens})