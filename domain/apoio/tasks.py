"""
from Celery import shared_task
from django.utils import timezone
from domain.apoio.models import Apoio
from domain.apoio.services import encerrar_apoio_automatico

@shared_task
def encerrar_apoios_sem_hospedagem():
    hoje = timezone.localdate()
    apoios = Apoio.objects.filter(
        status=True,
        dataInicio=hoje,
        checkOut__isnull=True
    ).select_related("paciente")

    encerrados = 0
    for apoio in apoios:
        encerrar_apoio_automatico(apoio)
        encerrados += 1
 
    return f"{encerrados} apoio(s) encerrado(s) automaticamente."
"""