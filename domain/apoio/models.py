from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from domain.pessoa.models import Pessoa
from domain.quarto.models import Quarto
from domain.solicitacao.models import SolicitantePessoa

class Apoio(models.Model):
    DATAFIM_CHOICES=[('HOJE', 'Hoje'),('DATA','Data'),('INDETERMINADO','Indeterminado')]
    motivo = models.CharField(max_length=500)
    paciente = models.ForeignKey(Pessoa, on_delete=models.PROTECT, related_name="pacientes")
    solicitante = models.ForeignKey(SolicitantePessoa, on_delete=models.PROTECT, null=True, blank=True, related_name="solicitantes")
#-- casaApoio = models.ForeignKey(CasaApoio,)
    dataInicio = models.DateField()
    previsaoFim_tipo = models.CharField(max_length=50, choices=DATAFIM_CHOICES)
    previsaoFim = models.DateField(null=True, blank=True)
    checkIn = models.DateTimeField(null=True, blank=True)
    checkOut = models.DateTimeField(null=True, blank=True)
    status = models.BooleanField(default=True, verbose_name="Status do Apoio")

    def clean(self):
        agora = timezone.now()

        if not self.dataInicio:
            self.dataInicio = agora

        if self.checkOut and not self.checkIn:
            raise ValidationError("faça checkIn antes de fazer checkOut")
        
        if self.checkOut and self.checkIn and self.checkOut < self.checkIn:
            raise ValidationError("checkOut não tem data anterior a checkIn")
    
        if not self.previsaoFim_tipo:
            self.previsaoFim_tipo = 'HOJE'

        if self.previsaoFim_tipo == 'DATA':
            if not self.previsaoFim:
                raise ValidationError("informe a data da previsão de fim")

        if self.previsaoFim and self.dataInicio and self.previsaoFim < self.dataInicio:
            raise ValidationError("a data prevista de fim não pode ser anterior a data de inicio")
    
        #RN: Uma pessoa não pode ser vinculada como paciente em outro apoio.       
        eh_paciente = Apoio.objects.filter(
            paciente = self.paciente,
            checkOut__isnull= True
         ).exclude(pk=self.pk)
        if eh_paciente.exists():
            raise ValidationError(f"{self.paciente.nome_pessoa} é paciente em outro apoio")
        
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def fazer_checkin(self):
        agora = timezone.now()
        self.checkIn = agora
        self.save()
    
    @property
    def acompanhante_atual(self):
        return self.acompanhantes.filter(checkOut__isnull=True).first()
    
    #RN: checkout do paciente representa fim do apoio e faz checkout do acompanhante vinculado no momento.
    def fazer_checkout(self, momento=None):
        acompanhante_ativo = self.acompanhante_atual
        agora = momento or timezone.now()
        if acompanhante_ativo and acompanhante_ativo.checkOut is None:
            acompanhante_ativo.checkOut = agora
            acompanhante_ativo.save()
        self.checkOut = agora
        self.status = False
        self.save()
    
    def __str__(self):
        return self.paciente.nome_pessoa

class HistoricoPacienteApoio(models.Model):
    apoio = models.OneToOneField(Apoio, on_delete=models.PROTECT, related_name="historico_apoio")
    pessoa = models.ForeignKey(Pessoa, on_delete=models.PROTECT, related_name="historico_pessoa")
    nome_pessoa = models.CharField(max_length=30)
    cpf_pessoa = models.CharField(max_length=11)
    inicio_apoio = models.DateField()
    checkIn_paciente = models.DateTimeField()
    encerramento_apoio = models.DateTimeField()
    pais = models.CharField(max_length=15, null=False, blank=False)
    cep = models.CharField(max_length=9)
    estado = models.CharField(max_length=2, null=False, blank=False)
    cidade = models.CharField(max_length=100, null=False, blank=False)
    bairro = models.CharField(max_length=100, null=False, blank=False)
    logradouro = models.CharField(max_length=200, null=False, blank=False)
    numero = models.CharField(max_length=20)
    complemento = models.CharField(max_length=50, blank=True)
    descricao = models.CharField(max_length=200, blank=True)

class Acompanhante(models.Model):
    VINCULO_CHOICES = [('PAI_MAE', 'Pai ou Mãe'),('CONJUGUE', 'Conjugue'), ('OUTROS', 'Outros')]
    apoio = models.ForeignKey(Apoio, on_delete=models.CASCADE, related_name="acompanhantes")
    nomeAcompanhante = models.ForeignKey(Pessoa, on_delete=models.CASCADE, related_name="vinculos_acompanhantes")
    vinculo = models.CharField(max_length=10, choices=VINCULO_CHOICES)
    descricaoVinculo = models.CharField(max_length=50, blank=True)
    checkIn = models.DateTimeField(default = timezone.now)
    checkOut = models.DateTimeField(null=True, blank=True)

    def clean(self):
        if self.vinculo == "Outros":
            if not self.descricaoVinculo:
                raise ValidationError("Descreva o vinculo do acompanhante com o paciente")
    
        #RN: Uma pessoa não pode ser vinculada como acompanhante em mais de um apoio ativo simultaneamente.       
        eh_acompanhante = Acompanhante.objects.filter(
            nome = self.nomeAcompanhante,
            checkOut__isnull= True
         ).exclude(pk=self.pk)
        if eh_acompanhante.exists():
            raise ValidationError(f"{self.nomeAcompanhante.nome_pessoa} ja é acompanhante de um apoio")
    
    def fazer_checkOut_acompanhante(self):
        agora = timezone.now()
        self.checkOut = agora
        self.save()

#hospedagem controla o tempo que
class Hospedagem(models.Model):
    observacao = models.CharField(max_length=500, null=True, blank=True)
    apoio = models.OneToOneField(Apoio, on_delete=models.CASCADE, related_name="hospedagem")
    
    def __str__(self):
        return self.apoio.paciente.nome_pessoa

#alocação controla a hospedagem e todos os quartos que ela passou,
#visto que uma hospedagem pode mudar de quarto 1 ou mais vezes
class AlocacaoQuarto(models.Model):
    hospedagem = models.ForeignKey(Hospedagem, on_delete=models.CASCADE, related_name="hospedagem_alocacao")
    quarto = models.ForeignKey(Quarto, on_delete=models.PROTECT, related_name="quarto_alocacao")
    inicioLocacao = models.DateField()
    fimLocacao = models.DateField(null=True, blank=True)
    
    def encerra_alocacao(self):
        agora = timezone.now()
        self.fimLocacao = agora
        self.save()

    def __str__(self):
        return f"Paciente:{self.hospedagem}-Quarto:{self.quarto}"
    
    @property
    def alocacao_atual(self):
        return self.quarto_alocacao.filter(checkOut__isnull=True).first()

class AnexoAcompanhante(models.Model):
    EXTENSAO_CHOICES = [('PDF', 'Pdf'), ('FOTO', 'Foto')]
    acompanhante = models.OneToOneField(Acompanhante, on_delete=models.SET_NULL, null=True, blank=True, related_name="anexos")
    nome = models.CharField(max_length=50)
    tipo = models.CharField(max_length=10, choices=EXTENSAO_CHOICES, default='Pdf')
    arquivo = models.FileField(upload_to="arquivos/autorazacoes_acompanhante")
    dataUpload = models.DateTimeField(auto_now_add=True)
    dataAlteracao = models.DateTimeField(auto_now=True)

    #RN: Paciente menor de idade precisa de acompanhante, e acompanhante de vinculo "outros" precisa ter
    #anexo de autoriação para acompanhamento
    def clean(self):
        if not self.acompanhante:
            return
        paciente = self.acompanhante.apoio.paciente

        if paciente.eh_menor_idade() and self.acompanhante.vinculo == "Outros":
            if not self.arquivo:
                raise ValidationError("Anexe a autorização de acompanhante para menor com outros tipos de vinculos")
            
            nome = self.arquivo.name.lower()
            if not (nome.endswith(".pdf") or nome.endswith(".jpg") or nome.endswith(".jpeg") or nome.endswith(".png")):
                raise ValidationError("Arquivo deve ser PDF ou imagem (JPG/PNG).")

    def __str__(self):
        return f"{self.nome}(apoio: {self.acomapanhante})"
    
class AnexoApoio(models.Model):
    EXTENSAO_CHOICES = [('PDF', 'Pdf'), ('FOTO', 'Foto')]
    apoio = models.ForeignKey(Apoio, on_delete=models.PROTECT, related_name="anexos")
    nome = models.CharField(max_length=50)
    tipo = models.CharField(max_length=10, choices=EXTENSAO_CHOICES, default='Pdf')
    arquivo = models.FileField(upload_to="arquivos/apoios")
    dataUpload = models.DateTimeField(auto_now_add=True)
    dataAlteracao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nome}(apoio: {self.apoio})"



