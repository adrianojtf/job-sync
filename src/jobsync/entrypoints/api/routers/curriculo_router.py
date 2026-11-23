"""Router de domínio de currículo para a API v1."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from jobsync.entrypoints.api.autorizacao import exigir_perfil_da_requisicao
from jobsync.curriculo import (
    ContextoVaga,
    RascunhoCurriculoAdaptado,
    SecaoCurriculo,
    TipoSecao,
)
from jobsync.curriculo.service_layer.adaptar_curriculo_para_vaga import (
    AdaptarCurriculoParaVagaInputDto,
)
from jobsync.curriculo.service_layer.gerar_pdf_curriculo_revisado import (
    GerarPdfCurriculoRevisado,
    GerarPdfCurriculoRevisadoInputDto,
    GerarPdfCurriculoRevisadoOutputDto,
)
from jobsync.curriculo.service_layer.identificar_lacunas_da_vaga import (
    IdentificarLacunasDaVagaInputDto,
)
from jobsync.curriculo_salvo.service_layer.remover_curriculo_salvo.service import (
    CurriculoSalvoNaoEncontrado,
)
from jobsync.curriculo_salvo.service_layer.salvar_curriculo import SalvarCurriculo
from jobsync.entrypoints.api.curriculo_pre_montado import (
    buscar_perfil_estruturado,
    historico_do_candidato,
    resolver_fonte_do_curriculo,
)
from jobsync.entrypoints.api.dependencies import (
    ServiceBuscarCurriculoAdaptadoDep,
    ServiceAdaptarCurriculoDep,
    ServiceAnalisarAtsVagaDep,
    ServiceAvaliarExperienciaDep,
    ServiceBuscarPerfilEstruturadoDep,
    ServiceGerarCartaApresentacaoDep,
    ServiceGerarPdfCurriculoRevisadoDep,
    ServiceIdentificarLacunasDaVagaDep,
    ServiceListarCurriculosSalvosDep,
    ServiceRemoverCurriculoSalvoDep,
    ServiceSalvarCurriculoDep,
    ServiceSugerirAjusteExperienciaAdaptadaDep,
    ServiceSugerirAjusteExperienciaDep,
    ServiceSugerirAjusteSecaoCurriculoDep,
)
from jobsync.entrypoints.api.schemas.curriculo import (
    AdaptarCurriculoRequest,
    AdaptarCurriculoResponse,
    AvaliacaoExperienciaResponse,
    AvaliarExperienciaRequest,
    AnalisarAtsRequest,
    AnalisarAtsResponse,
    CartaApresentacaoResponse,
    CurriculoRevisadoResponse,
    CurriculoSalvarRequest,
    CurriculoSalvoConteudoResponse,
    CurriculoSalvoResponse,
    CurriculosListagemResponse,
    GerarCartaApresentacaoRequest,
    GerarPdfCurriculoRevisadoRequest,
    RascunhoAdaptadoResponse,
    SugerirAjusteExperienciaAdaptadaRequest,
    SugerirAjusteExperienciaAdaptadaResponse,
    SugerirAjusteExperienciaRequest,
    SugerirAjusteExperienciaResponse,
    SugerirAjusteSecaoRequest,
    SugerirAjusteSecaoResponse,
)
from jobsync.entrypoints.api.schemas.erro import ProblemaResponse
from jobsync.entrypoints.api.schemas.lacunas import LacunasRequest, LacunasResponse
from jobsync.vaga import AnaliseVaga

router = APIRouter(tags=["currículos"], dependencies=[Depends(exigir_perfil_da_requisicao)])


@router.post(
    "/experiencias-profissionais/avaliacoes",
    response_model=AvaliacaoExperienciaResponse,
    status_code=status.HTTP_200_OK,
    summary="Avaliar experiência profissional",
    description=(
        "Avalia uma experiência em relação a uma vaga-alvo. "
        "O texto e o resultado não são persistidos nem alterados."
    ),
    responses={
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": ProblemaResponse,
            "description": "Experiência ou descrição da vaga ausente ou inválida.",
        },
        status.HTTP_502_BAD_GATEWAY: {
            "model": ProblemaResponse,
            "description": "O provedor de avaliação está indisponível.",
        },
    },
)
def avaliar_experiencia(
    body: AvaliarExperienciaRequest,
    service: ServiceAvaliarExperienciaDep,
) -> AvaliacaoExperienciaResponse:
    """Retorna score e categorias estruturadas para uma experiência profissional."""
    avaliacao = service.executar(body.to_dto())
    return AvaliacaoExperienciaResponse.from_domain(avaliacao)


@router.post(
    "/curriculos",
    response_model=CurriculoSalvoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Salvar currículo",
    description="Salva um currículo PDF na biblioteca de um perfil.",
)
def salvar_curriculo(
    body: CurriculoSalvarRequest,
    service: ServiceSalvarCurriculoDep,
    response: Response,
    request: Request,
) -> CurriculoSalvoResponse:
    """Salva um novo currículo na biblioteca do perfil informado."""
    try:
        salvo = service.executar(body.to_dto())
    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(erro),
        )
    location = f"{request.url.path}/{salvo.id}"
    response.headers["Location"] = location
    return CurriculoSalvoResponse.from_dto(salvo)


@router.get(
    "/curriculos",
    response_model=CurriculosListagemResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar currículos salvos",
    description="Lista todos os currículos salvos de um perfil.",
)
def listar_curriculos(
    perfil_identificador: str,
    service: ServiceListarCurriculosSalvosDep,
) -> CurriculosListagemResponse:
    """Lista os currículos salvos de um perfil."""
    curriculos = service.executar(perfil_identificador)
    return CurriculosListagemResponse.from_dto(curriculos)


@router.get(
    "/curriculos/{id}",
    response_model=CurriculoSalvoResponse,
    status_code=status.HTTP_200_OK,
    summary="Obter currículo",
    description="Retorna os metadados de um currículo salvo.",
)
def obter_curriculo(
    id: str,
    perfil_identificador: str,
    service: ServiceListarCurriculosSalvosDep,
) -> CurriculoSalvoResponse:
    """Retorna um currículo salvo pelo identificador e perfil."""
    curriculos = service.executar(perfil_identificador)
    for curriculo in curriculos:
        if curriculo.id == id:
            return CurriculoSalvoResponse.from_dto(curriculo)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Currículo não encontrado.",
    )


@router.get(
    "/curriculos/{id}/conteudo",
    response_model=CurriculoSalvoConteudoResponse,
    status_code=status.HTTP_200_OK,
    summary="Baixar conteúdo do currículo",
    description="Retorna o PDF de um currículo salvo codificado em base64.",
)
def obter_conteudo_curriculo(
    id: str,
    perfil_identificador: str,
    service: ServiceListarCurriculosSalvosDep,
) -> CurriculoSalvoConteudoResponse:
    """Retorna o conteúdo PDF de um currículo salvo."""
    curriculos = service.executar(perfil_identificador)
    for curriculo in curriculos:
        if curriculo.id == id:
            return CurriculoSalvoConteudoResponse.from_dto(curriculo)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Currículo não encontrado.",
    )


@router.delete(
    "/curriculos/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover currículo",
    description="Remove um currículo salvo da biblioteca do perfil.",
)
def remover_curriculo(
    id: str,
    perfil_identificador: str,
    service: ServiceRemoverCurriculoSalvoDep,
) -> Response:
    """Remove um currículo salvo pelo identificador e perfil."""
    try:
        service.executar(id, perfil_identificador)
    except CurriculoSalvoNaoEncontrado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Currículo não encontrado.",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/cartas-apresentacao",
    response_model=CartaApresentacaoResponse,
    status_code=status.HTTP_200_OK,
    summary="Gerar carta de apresentação",
    description="Gera uma carta de apresentação para uma vaga e currículo/perfil.",
)
def gerar_carta_apresentacao(
    body: GerarCartaApresentacaoRequest,
    adaptar: ServiceAdaptarCurriculoDep,
    gerar: ServiceGerarCartaApresentacaoDep,
    buscar_perfil: ServiceBuscarPerfilEstruturadoDep,
    buscar_adaptado: ServiceBuscarCurriculoAdaptadoDep,
) -> CartaApresentacaoResponse:
    """Gera uma carta de apresentação personalizada para a vaga."""
    fonte = resolver_fonte_do_curriculo(
        body.perfil_identificador,
        body.curriculo_adaptado_id,
        body.pdf_base64,
        buscar_perfil,
        buscar_adaptado,
    )
    try:
        output = adaptar.executar(body.to_dto(curriculo_pre_montado=fonte.curriculo))
    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(erro),
        )
    carta = gerar.executar(
        output.curriculo_adaptado, output.analise_vaga, body.idioma_alvo
    )
    return CartaApresentacaoResponse(carta=carta)


@router.post(
    "/curriculos/{id}/adaptacoes",
    response_model=AdaptarCurriculoResponse,
    status_code=status.HTTP_200_OK,
    summary="Adaptar currículo para vaga",
    description="Gera um currículo adaptado a uma vaga específica. Use ?download=true para receber o PDF em binário.",
)
def adaptar_curriculo(
    id: str,
    body: AdaptarCurriculoRequest,
    service: ServiceAdaptarCurriculoDep,
    gerar_pdf: ServiceGerarPdfCurriculoRevisadoDep,
    buscar_perfil: ServiceBuscarPerfilEstruturadoDep,
    buscar_adaptado: ServiceBuscarCurriculoAdaptadoDep,
    download: bool = False,
) -> AdaptarCurriculoResponse | Response:
    """Adapta o currículo à descrição da vaga e gera o PDF sem revisão (fluxo legado)."""
    fonte = resolver_fonte_do_curriculo(
        body.perfil_identificador,
        None,
        body.pdf_base64,
        buscar_perfil,
        buscar_adaptado,
    )
    try:
        input_dto = body.to_dto(
            curriculo_pre_montado=fonte.curriculo,
            experiencias_profissionais=fonte.experiencias,
        )
        output = service.executar(input_dto)
        pdf = _gerar_pdf_sem_revisao(gerar_pdf, input_dto, output.rascunho)
    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(erro),
        )
    if download:
        return _resposta_pdf(pdf)
    return AdaptarCurriculoResponse.from_dto(output, pdf)


def _gerar_pdf_sem_revisao(
    gerar_pdf: GerarPdfCurriculoRevisado,
    input_dto: AdaptarCurriculoParaVagaInputDto,
    rascunho: RascunhoCurriculoAdaptado,
) -> GerarPdfCurriculoRevisadoOutputDto:
    return gerar_pdf.executar(
        GerarPdfCurriculoRevisadoInputDto(
            rascunho=rascunho,
            idioma_alvo=input_dto.idioma_alvo,
            cargo_alvo=input_dto.cargo_alvo,
            empresa_alvo=input_dto.empresa_alvo,
            data_referencia=input_dto.data_referencia,
        )
    )


def _resposta_pdf(pdf: GerarPdfCurriculoRevisadoOutputDto) -> Response:
    return Response(
        content=pdf.pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{pdf.nome_arquivo.valor}"'
        },
    )


@router.post(
    "/curriculos/lacunas",
    response_model=LacunasResponse,
    status_code=status.HTTP_200_OK,
    summary="Identificar lacunas da vaga",
    description=(
        "Compara a vaga com o perfil estruturado e devolve até 5 temas centrais que o perfil não "
        "sustenta, cada um com uma pergunta. Lista vazia quando não há o que perguntar ou a IA "
        "está indisponível: a geração do currículo nunca depende desta etapa."
    ),
    responses={
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": ProblemaResponse,
            "description": "Perfil inexistente ou dados da vaga inválidos.",
        },
    },
)
def identificar_lacunas(
    body: LacunasRequest,
    service: ServiceIdentificarLacunasDaVagaDep,
    buscar_perfil: ServiceBuscarPerfilEstruturadoDep,
) -> LacunasResponse:
    """Aponta os temas da vaga que o perfil não mostra, para o candidato responder antes da geração."""
    perfil = buscar_perfil_estruturado(body.perfil_identificador, buscar_perfil)
    try:
        contexto = ContextoVaga(
            descricao_vaga=body.descricao_vaga,
            idioma_alvo=body.idioma_alvo,
            analise_vaga=AnaliseVaga(requisitos=(), ambiguidade=(), texto_original=body.descricao_vaga),
            cargo_alvo=body.cargo_alvo,
        )
    except ValueError as erro:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(erro))
    lacunas = service.executar(
        IdentificarLacunasDaVagaInputDto(historico=historico_do_candidato(perfil), contexto=contexto)
    )
    return LacunasResponse.from_dto(lacunas)


@router.post(
    "/curriculos/{id}/rascunhos-adaptados",
    response_model=RascunhoAdaptadoResponse,
    status_code=status.HTTP_200_OK,
    summary="Gerar rascunho do currículo adaptado",
    description=(
        "Adapta o currículo à vaga via IA e devolve o conteúdo organizado por seção "
        "para revisão. Não gera PDF nem persiste o rascunho."
    ),
    responses={
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": ProblemaResponse,
            "description": "Dados da vaga ou fonte do currículo ausentes ou inválidos.",
        },
    },
)
def gerar_rascunho_adaptado(
    id: str,
    body: AdaptarCurriculoRequest,
    service: ServiceAdaptarCurriculoDep,
    buscar_perfil: ServiceBuscarPerfilEstruturadoDep,
    buscar_adaptado: ServiceBuscarCurriculoAdaptadoDep,
) -> RascunhoAdaptadoResponse:
    """Adapta o currículo à vaga e devolve o rascunho para revisão."""
    fonte = resolver_fonte_do_curriculo(
        body.perfil_identificador,
        body.curriculo_adaptado_id,
        body.pdf_base64,
        buscar_perfil,
        buscar_adaptado,
    )
    try:
        output = service.executar(
            body.to_dto(
                curriculo_pre_montado=fonte.curriculo,
                experiencias_profissionais=fonte.experiencias,
            )
        )
    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(erro),
        )
    return RascunhoAdaptadoResponse.from_dto(output)


@router.post(
    "/curriculos-revisados",
    response_model=CurriculoRevisadoResponse,
    status_code=status.HTTP_200_OK,
    summary="Gerar PDF do currículo revisado",
    description=(
        "Gera o PDF a partir do rascunho revisado e confirmado pelo usuário, sem nova "
        "chamada à IA. Use ?download=true para receber o PDF em binário."
    ),
    responses={
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": ProblemaResponse,
            "description": "Rascunho ou dados da vaga inválidos.",
        },
    },
)
def gerar_pdf_curriculo_revisado(
    body: GerarPdfCurriculoRevisadoRequest,
    service: ServiceGerarPdfCurriculoRevisadoDep,
    download: bool = False,
) -> CurriculoRevisadoResponse | Response:
    """Gera o PDF do currículo a partir do conteúdo revisado."""
    try:
        pdf = service.executar(body.to_dto())
    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(erro),
        )
    if download:
        return _resposta_pdf(pdf)
    return CurriculoRevisadoResponse.from_dto(pdf)


_RESPOSTAS_SUGESTAO = {
    status.HTTP_422_UNPROCESSABLE_ENTITY: {
        "model": ProblemaResponse,
        "description": "Texto, seção ou contexto da vaga ausentes ou inválidos.",
    },
    status.HTTP_502_BAD_GATEWAY: {
        "model": ProblemaResponse,
        "description": "O provedor de IA está indisponível.",
    },
}


@router.post(
    "/secoes-curriculo/sugestoes",
    response_model=SugerirAjusteSecaoResponse,
    status_code=status.HTTP_200_OK,
    summary="Sugerir ajuste de uma seção",
    description=(
        "Sugere, via IA, uma nova versão do texto de uma seção (perfil, tecnologias ou "
        "experiências). Com contexto de vaga adapta o texto à vaga; sem ele, melhora a "
        "escrita. Nada é persistido nem alterado."
    ),
    responses=_RESPOSTAS_SUGESTAO,
)
def sugerir_ajuste_secao(
    body: SugerirAjusteSecaoRequest,
    service: ServiceSugerirAjusteSecaoCurriculoDep,
) -> SugerirAjusteSecaoResponse:
    """Devolve o texto sugerido para a seção informada."""
    try:
        secao = SecaoCurriculo(
            tipo=TipoSecao[body.secao.tipo],
            titulo=body.secao.titulo,
            conteudo=body.secao.conteudo,
        )
        contexto = body.contexto_vaga.to_domain() if body.contexto_vaga else None
        sugerida = service.executar(secao, contexto, body.refino.to_domain())
    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(erro),
        )
    return SugerirAjusteSecaoResponse(conteudo_sugerido=sugerida.valor.conteudo, foco=sugerida.foco)


@router.post(
    "/experiencias-profissionais/sugestoes",
    response_model=SugerirAjusteExperienciaResponse,
    status_code=status.HTTP_200_OK,
    summary="Sugerir ajuste de uma experiência",
    description=(
        "Sugere, via IA, uma nova descrição para uma experiência do perfil, melhorando a "
        "escrita sem vaga-alvo. Para adaptar à vaga, use POST /v1/experiencias-adaptadas/"
        "sugestoes. Cargo, empresa e período não são alterados, e nada é persistido."
    ),
    responses=_RESPOSTAS_SUGESTAO,
)
def sugerir_ajuste_experiencia(
    body: SugerirAjusteExperienciaRequest,
    service: ServiceSugerirAjusteExperienciaDep,
) -> SugerirAjusteExperienciaResponse:
    """Devolve a descrição sugerida para a experiência do perfil informada."""
    try:
        sugerida = service.executar(body.experiencia.to_domain(), body.refino.to_domain())
    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(erro),
        )
    return SugerirAjusteExperienciaResponse(
        descricao_sugerida=sugerida.valor.descricao, foco=sugerida.foco
    )


@router.post(
    "/experiencias-adaptadas/sugestoes",
    response_model=SugerirAjusteExperienciaAdaptadaResponse,
    status_code=status.HTTP_200_OK,
    summary="Sugerir ajuste de uma experiência adaptada",
    description=(
        "Sugere, via IA, conquistas e contexto novos para uma experiência do currículo adaptado, "
        "partindo dos textos atuais e orientado pela vaga. Cargo, empresa e período não são "
        "alterados, e nada é persistido."
    ),
    responses=_RESPOSTAS_SUGESTAO,
)
def sugerir_ajuste_experiencia_adaptada(
    body: SugerirAjusteExperienciaAdaptadaRequest,
    service: ServiceSugerirAjusteExperienciaAdaptadaDep,
) -> SugerirAjusteExperienciaAdaptadaResponse:
    """Devolve conquistas e contexto sugeridos para a experiência informada."""
    try:
        sugerida = service.executar(
            body.experiencia.to_domain(), body.contexto_vaga.to_domain(), body.refino.to_domain()
        )
    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(erro),
        )
    return SugerirAjusteExperienciaAdaptadaResponse(
        conquistas=list(sugerida.valor.conquistas),
        contexto=sugerida.valor.contexto,
        foco=sugerida.foco,
    )


@router.post(
    "/curriculos/{id}/analises-ats",
    response_model=AnalisarAtsResponse,
    status_code=status.HTTP_200_OK,
    summary="Analisar aderência ATS",
    description="Analisa a aderência do currículo à vaga sem gerar PDF adaptado.",
)
def analisar_ats(
    id: str,
    body: AnalisarAtsRequest,
    service: ServiceAnalisarAtsVagaDep,
    buscar_perfil: ServiceBuscarPerfilEstruturadoDep,
    buscar_adaptado: ServiceBuscarCurriculoAdaptadoDep,
) -> AnalisarAtsResponse:
    """Retorna nota, requisitos faltantes e sugestões de melhoria ATS."""
    fonte = resolver_fonte_do_curriculo(
        body.perfil_identificador,
        body.curriculo_adaptado_id,
        body.pdf_base64,
        buscar_perfil,
        buscar_adaptado,
    )
    try:
        output = service.executar(body.to_dto(curriculo_pre_montado=fonte.curriculo))
    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(erro),
        )
    return AnalisarAtsResponse.from_dto(output)
