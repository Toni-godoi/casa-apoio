from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import date, time, datetime, timedelta
from domain.apoio.models import Apoio, Acompanhante, Hospedagem, AlocacaoQuarto, HistoricoPacienteApoio, AnexoAcompanhante, AnexoApoio
from domain.pessoa.models import Pessoa
from domain.solicitacao.models import SolicitantePessoa
from domain.quarto.models import Quarto
from typing import Optional
    
@transaction.atomic
def iniciar_apoio(
    *,
    #casa_apoio
    motivo_apoio:str,
    data_inicio:date,
    previsaoFim_tipo:str = 'HOJE',
    previsao_fim:Optional[date]=None,
    paciente_id:int,
    checkIn:bool = False,
    acompanhante_id:Optional[int]=None,
    tipoVinculo_acompanhante:str,
    descricao_vinculo:str,
    solicitante_id:Optional[int]=None,
    descHospedagem:Optional[str]=None,
    quarto_id:Optional[int]=None,
    inicio_alocacao:Optional[date]=None,
    nome_anexo:str,
    anexo = None
)->Apoio:
    
    paciente = _existe_pessoa(paciente_id, "Paciente")
    _previsao_fim_data(previsaoFim_tipo, previsao_fim)

    if paciente:
        _validar_paciente_com_apoio(paciente_id, "Paciente")
        _validar_se_paciente_menor(paciente, acompanhante_id, tipoVinculo_acompanhante, descricao_vinculo)

    apoio_hospedagem = _valida_solicitante_hospedagem(solicitante_id, previsaoFim_tipo)

    solicitante_pessoa = None
    if solicitante_id:
        solicitante_pessoa = _valida_solicitante_existe(solicitante_id)
        
    apoio = Apoio(
        motivo=motivo_apoio,
        paciente=paciente,
        dataInicio=data_inicio,
        previsaoFim_tipo=previsaoFim_tipo,
        previsaoFim=previsao_fim,
        solicitante=solicitante_pessoa,
        status = True,
    )

    apoio.save()

    if anexo:
        if not nome_anexo:
            raise ValidationError("Nome para o arquivo anexo é obrigatório")
        else:
            anexo = AnexoApoio(
                apoio = apoio,
                nome_arquivo = nome_anexo,
                arquivo = anexo
            )
            anexo.save()
    
    if checkIn:
        checkIn_apoio(apoio.pk)

    #se existe um acompanhante informado, ele ja foi validado acima. Aqui, criamos ele.
    if acompanhante_id:
        _validar_acompanhante_apto(acompanhante_id, tipoVinculo_acompanhante, descricao_vinculo)
        vincular_acompanhante(
            apoio=apoio,
            acompanhante_id=acompanhante_id,
            tipoVinculo_acompanhante=tipoVinculo_acompanhante,
            descricao_vinculo=descricao_vinculo
        )

    #aqui vou criar evolução para hospedagem com base em previsãoFim_tipo.
    if apoio_hospedagem == True:
        _validar_quarto_ativo(quarto_id)
        iniciar_hospedagem(
            apoio=apoio,
            descHospedagem=descHospedagem,
            quarto_id=quarto_id,
            inicio_alocacao=inicio_alocacao
        )
    return apoio

@transaction.atomic
def vincular_acompanhante(
    *,
    apoio:Apoio,
    acompanhante_id:int,
    tipoVinculo_acompanhante:str = "",
    descricao_vinculo:str = "",
)->Acompanhante:
    
    acompanhante_pessoa = _existe_pessoa(acompanhante_id, "Acompanhante")
    agora = timezone.now()
    if acompanhante_pessoa:
        _validar_paciente_com_apoio(acompanhante_id, "Acompanhante")
        _validar_acompanhante_livre(acompanhante_id)
        _validar_apoioTem_acompanhante(apoio)
        
    if not tipoVinculo_acompanhante:
        raise ValidationError("Informe o vinculo do acompanhante")
    if tipoVinculo_acompanhante: 
        if tipoVinculo_acompanhante != 'OUTROS':
            descricao_vinculo = tipoVinculo_acompanhante
        if tipoVinculo_acompanhante == 'OUTROS' and not descricao_vinculo:
            raise ValidationError("Descreva o vinculo do acompanhante")

    acompanhante = Acompanhante(
        apoio = apoio,
        nomeAcompanhante = acompanhante_pessoa,
        vinculo = tipoVinculo_acompanhante,
        descricaoVinculo = descricao_vinculo,
        checkIn=agora
    )
    acompanhante.save()
    return acompanhante

@transaction.atomic
def editar_apoio(
    *,
    apoio_id: int,
    motivo_apoio: str,
    previsaoFim_tipo: str,
    previsao_fim,
    solicitante_id: int = None,
    descHospedagem: str = "",
    quarto_id: int = None,
    inicio_alocacao:Optional[date]=None,
    ed_anexo=None,
    remover_anexo=False,
    nome_anexo=str
):

    apoio = Apoio.objects.get(pk=apoio_id)
    if not apoio.status:
        raise ValidationError("Apoio já finalizado não pode ser editado")
    
    hoje = timezone.localdate()
    if previsaoFim_tipo == 'HOJE' and apoio.dataInicio != hoje:
        raise ValidationError("Apoio ja recebeu HOSPEDAGEM. Defina tipo DATA e selecione a data para encerramento")
    
    _previsao_fim_data(previsaoFim_tipo, previsao_fim)

    # estado antes/depois
    era_hospedagem = apoio.previsaoFim_tipo != "HOJE"
    agora_hospedagem = previsaoFim_tipo != "HOJE"

    if not era_hospedagem and previsaoFim_tipo == "HOJE" and quarto_id:
        raise ValidationError("Apoio que finaliza hoje não pode ter quarto")

    #atualiza dados simples
    apoio.motivo = motivo_apoio
    apoio.previsaoFim_tipo = previsaoFim_tipo
    apoio.previsaoFim = previsao_fim
    apoio.solicitante_id = solicitante_id

    # NÃO ERA e agora VIROU HOSPEDAGEM
    if not era_hospedagem and agora_hospedagem:

        if not quarto_id:
            raise ValidationError("Selecione um quarto para hospedagem")

        hospedagem = Hospedagem.objects.create(
            apoio=apoio,
            observacao=descHospedagem
        )

        fazer_alocacao(
            hospedagem=hospedagem,
            quarto_id=quarto_id,
            inicio_alocacao=inicio_alocacao
        )

    # ERA e agora DEIXOU DE SER HOSPEDAGEM
    elif era_hospedagem and not agora_hospedagem:

        hospedagem = getattr(apoio, "hospedagem", None)

        if hospedagem:
            alocacao = hospedagem.hospedagem_alocacao.filter(
                fimLocacao__isnull=True
            ).first()

            if alocacao:
                alocacao.fimLocacao = timezone.now()
                alocacao.save()

                alocacao.quarto.liberar_vaga()

            hospedagem.delete()

    # CONTINUA SENDO HOSPEDAGEM
    elif era_hospedagem and agora_hospedagem:

        hospedagem = getattr(apoio, "hospedagem", None)

        if not hospedagem:
            raise ValidationError("Hospedagem não encontrada")

        # atualiza observação
        hospedagem.observacao = descHospedagem
        hospedagem.save()

        # troca de quarto (se informado)
        if quarto_id:

            atual = hospedagem.hospedagem_alocacao.filter(
                fimLocacao__isnull=True
            ).first()

            # só troca se mudou mesmo
            if atual and atual.quarto_id != quarto_id:

                atual.fimLocacao = timezone.now()
                atual.save()

                atual.quarto.liberar_vaga()

                fazer_alocacao(
                    hospedagem=hospedagem,
                    quarto_id=quarto_id,
                    inicio_alocacao=inicio_alocacao
                )
    apoio.save()

    anexo_atual = apoio.apoio_anexo.first()
    if remover_anexo:
        if anexo_atual:
            anexo_atual.delete()
    elif anexo_atual:
        if ed_anexo:
            # mudou o arquivo
            anexo_atual.arquivo = ed_anexo
        if nome_anexo:
            # mudou o nome ou manteve o nome informado
            anexo_atual.nome_arquivo = nome_anexo
        anexo_atual.save()
    elif ed_anexo:
        # não existia anexo e foi enviado um novo
        AnexoApoio.objects.create(
            apoio=apoio,
            arquivo=ed_anexo,
            nome_arquivo=nome_anexo
        )
    return apoio
    
@transaction.atomic
def iniciar_hospedagem(
    *,
    apoio:Apoio,
    descHospedagem:str,
    quarto_id:int,
    inicio_alocacao:date,
)->Hospedagem:
    
    quarto = _existe_quarto(quarto_id)
    vagas = quarto.verifica_vagasLivres()
    if vagas <= 0:
        raise ValidationError("sem vagas para o quarto")
    if vagas >= 1:
        hospedagem = Hospedagem(
            apoio=apoio,
            observacao=descHospedagem,
        )    
    hospedagem.save()

    fazer_alocacao(
        hospedagem=hospedagem,
        quarto_id=quarto_id,
        inicio_alocacao=inicio_alocacao,
    )
    return hospedagem

@transaction.atomic
def fazer_alocacao(
        *,
        hospedagem:Hospedagem,
        quarto_id:int,
        inicio_alocacao:date,
    )->AlocacaoQuarto:

    quarto = _existe_quarto(quarto_id)
    vagas = quarto.verifica_vagasLivres()
    if vagas <= 0:
        raise ValidationError("sem vagas para o quarto")
    if vagas >= 1:
        alocacao = AlocacaoQuarto(
            hospedagem = hospedagem,
            quarto = quarto,
            inicioLocacao=inicio_alocacao
        )
        quarto.preenche_vaga()
        alocacao.save()
    
    return alocacao
    
@transaction.atomic
def checkIn_apoio(apoio_id:int):
    apoio = Apoio.objects.filter(
        pk=apoio_id,
        status = True,
        checkIn__isnull=True
    ).first()
    if not apoio:
        raise ValidationError("apoio não encontrado")
    
    apoio.fazer_checkin()

@transaction.atomic
def checkOut_apoio(apoio_id:int):
    
    apoio = Apoio.objects.filter(
        pk=apoio_id,
        status = True,
        checkOut__isnull=True
        ).first()
    
    if not apoio:
        raise ValidationError("apoio já encerrado ou não encontrado")
    if apoio.checkIn == None:
        raise ValidationError("Não é possivel fazer checkout sem checkin")
    
    apoio.fazer_checkout()
    if hasattr(apoio, "hospedagem"):
        alocacao = apoio.hospedagem.hospedagem_alocacao.filter(
            fimLocacao__isnull=True
        ).first()
        if alocacao:
            alocacao.encerra_alocacao()
            alocacao.quarto.liberar_vaga()
    
    HistoricoPacienteApoio.objects.create(
        apoio=apoio,
        pessoa=apoio.paciente,
        nome_pessoa=apoio.paciente.nome_pessoa,
        cpf_pessoa=apoio.paciente.cpf_pessoa,
        inicio_apoio=apoio.dataInicio,
        checkIn_paciente=apoio.checkIn,
        encerramento_apoio=apoio.checkOut,
        pais=apoio.paciente.endereco.bairro.cidade.estado.pais,
        cep=apoio.paciente.endereco.cep,
        estado=apoio.paciente.endereco.bairro.cidade.estado,
        cidade=apoio.paciente.endereco.bairro.cidade,
        bairro=apoio.paciente.endereco.bairro,
        logradouro=apoio.paciente.endereco.logradouro,
        numero=apoio.paciente.endereco.numero,
        complemento=apoio.paciente.endereco.complemento,
        descricao=apoio.paciente.endereco.descricao
    )
    
@transaction.atomic
def checkout_acompanhante(acompanhante_id:int):
    acomp = Acompanhante.objects.filter(
        pk=acompanhante_id,
        checkIn__isnull=False,
        checkOut__isnull=True
    ).first()

    if not acomp:
        raise ValidationError("Acompanhante não encontrado")
    
    acomp.fazer_checkOut_acompanhante()

#Função quando chamada, encerra o apoio no horario definido - corrigir ainda
def encerrar_apoio_automatico(apoio: Apoio) -> None:
    if apoio.previsaoFim_tipo == 'HOJE' and apoio.status:
        encerramento = datetime.combine(apoio.dataInicio, time(23,59,59))
        encerramento = timezone.make_aware(encerramento)
        apoio.fazer_checkout(momento=encerramento)

###
#-- funções da regra de nogocio
###
#verifica se a pessoa que vai assumir papel esta cadastrado no sistema
def _existe_pessoa(pessoa:int, papel:str) -> Pessoa:
    try:
        return Pessoa.objects.get(pk=pessoa)
    except Pessoa.DoesNotExist:
        raise ValidationError(f"Não foi possivel econtrar {pessoa} para {papel}")

#validação: tipo previsão de fim = DATA, precisa ser informado uma data para previsão de fim
def _previsao_fim_data(tipo:str, fim_previsto:date)->None:
    
    hoje = timezone.now()
    if fim_previsto:
        if tipo == 'INDETERMINADO':
            raise ValidationError("apoio INDETERMINADO não se aplica data para fim")
        if tipo == 'HOJE':
            raise ValidationError("NÃO é necessário definir uma data para o apoio que encerra hoje")

    #tipo data precisa de uma data fornecida.
    if tipo == 'DATA': 
        if not fim_previsto:
            raise ValidationError("Informe a data de previsão do fim do apoio")
        #uma data previsa representa uma data futura e requer apoio com hospedagem
        if fim_previsto == hoje:
            raise ValidationError("A data previsa para fim do apoio não pode ser igual a hoje")

###
#-- funções da regra de nogocio - PACIENTES
###
#validação se pessoa já possui algum papel
def _validar_paciente_com_apoio(pessoa_pk:int, papel:str)->None:
    
    paciente = Apoio.objects.filter(
        paciente__pk=pessoa_pk,
        status=True,
        checkOut__isnull=True
    ).exists()
    acompanhante = Acompanhante.objects.filter(
        nomeAcompanhante__pk = pessoa_pk,
        checkOut__isnull = True,
        apoio__checkOut__isnull=True
    ).exists()

    if papel == "Paciente":
        if paciente:
            raise ValidationError(f"O {papel} escolhido ja é Paciente em outro apoio")
        if acompanhante:
            raise ValidationError(f"O {papel} escolhido ja é Acompanhante em outro apoio")
    if papel == "Acompanhante" and paciente:
        raise ValidationError(f"O {papel} escolhido ja é Paciente em outro apoio")

#validação de acompanhante e idade paciente
def _validar_se_paciente_menor(paciente: Pessoa, 
                            acompanhante_id:Optional[int]=None, 
                            vinculo:Optional[str]=None,
                            desc_vinculo:Optional[str]=None)->None:
    #saber se paciente é menor
    if paciente.eh_menor_idade():
        #paciente < 18, obrigatório acompanhante
        if not acompanhante_id:
            raise ValidationError("o paciente menor de idade precisa de acompanhante")
        if acompanhante_id:
            #validar se existe essa pessoa acompanhante
            acom = _existe_pessoa(acompanhante_id, "Acompanhante")
            #validar se se o acompanhante é maior de idade
            if acom.eh_menor_idade():
              raise ValidationError("Menor de idade não pode acompanhar outro menor")
            #paciente < 18, tem acompanhante, obrigatório vinculo
            if not vinculo:
                raise ValidationError("informe vinculo do acompanhante")
            if vinculo == "OUTROS" and not desc_vinculo:
                raise ValidationError("Descreva o vinculo do acompanhante")
                
###
#-- funções da regra de nogocio - ACOMPANHANTES
###
#validação de acompanhante para maiores
def _validar_acompanhante_apto(acompanhante_id:str, 
                            vinculo:str,
                            desc_vinculo:Optional[str])->None:
    #tem acompanhante, saber se existe como pessoa
    if acompanhante_id:
        acom = _existe_pessoa(acompanhante_id, "Acompanhante")

        _validar_paciente_com_apoio(acompanhante_id, "Acompanhante")

        #tem pessoa_acompanhante, precisa de tipo de vinculo
        if not vinculo:
            raise ValidationError("informe vinculo do acompanhante")
        #vinculo "outro", obrigatorio (acompanhante > 18 e descrição de vinculo)
        if vinculo == "OUTROS":
            if acom.eh_menor_idade():
                raise ValidationError("Neste caso, menor de idade não pode ser acompanhante")
            if not desc_vinculo:
                raise ValidationError("Descreva vinculo do acompanhante com o paciente")
        
#verificar se o acompanhante ja esta vinculado a algum apoio
def _validar_acompanhante_livre(acompanhante_pk:int)->None:

    existe = Acompanhante.objects.filter(
            nomeAcompanhante__pk=acompanhante_pk,
            apoio__status=True,
            checkOut__isnull=True
        )
    
    if existe.exists():
        raise ValidationError("O acompanhante ja esta vinculado com um apoio")
    
#verificar se o apoio ja tem acompanhante
def _validar_apoioTem_acompanhante(apoio: Apoio)->None:
    if apoio.acompanhantes.filter(checkOut__isnull=True).exists():
        raise ValidationError("O apoio ja possui acompanhante")

#validação: tipo Identerminado e Data correspondem a hospedagem. São obrigatórios terem solicitantes
def _valida_solicitante_hospedagem(solicitante_id:int, tipo:str)->bool:
    if tipo =='HOJE':
        return False
    if tipo == 'INDETERMINADO' or tipo == 'DATA':
        if not solicitante_id:
            raise ValidationError("Um apoio que precisa de hospedagem requer solicitante")
    return True
    
def _valida_solicitante_existe(solicitante_pk:int)->SolicitantePessoa:
    solicitante = SolicitantePessoa.objects.filter(
        pk=solicitante_pk,
    ).first()
    if not solicitante:
        raise ValidationError("Solicitante não existe")
    
    return solicitante
###
#-- funções da regra de nogocio - HOSPEDAGENS
###
def _existe_quarto(quarto_id:int)->Quarto:
    try:
        return Quarto.objects.get(pk=quarto_id)
    except Quarto.DoesNotExist:
        raise ValidationError("Quarto não encontrado")
    
def _validar_quarto_ativo(quarto_id:int)->None:
    if not Quarto.objects.filter(
        pk=quarto_id,
        status=True
    ).exists():
        raise ValidationError("Quarto inválido para hospedagem")