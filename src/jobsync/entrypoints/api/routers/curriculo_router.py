"""Router de domínio de currículo para a API v1."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, Response, status

from jobsync.curriculo import Curriculo
from jobsync.curriculo_salvo.service_layer.remover_curriculo_salvo.service import (
    CurriculoSalvoNaoEncontrado,
)
from jobsync.curriculo_salvo.service_layer.salvar_curriculo import SalvarCurriculo
from jobsync.entrypoints.api.dependencies import (
    ServiceAdaptarCurriculoDep,
    ServiceAnalisarAtsVagaDep,
    ServiceBuscarPerfilEstruturadoDep,
    ServiceGerarCartaApresentacaoDep,
    ServiceListarCurriculosSalvosDep,
    ServiceRemoverCurriculoSalvoDep,
    ServiceSalvarCurriculoDep,
)
from jobsync.entrypoints.api.schemas.curriculo import (
    AdaptarCurriculoRequest,
    AdaptarCurriculoResponse,
    AnalisarAtsRequest,
    AnalisarAtsResponse,
    CartaApresentacaoResponse,
    CurriculoSalvarRequest,
    CurriculoSalvoConteudoResponse,
    CurriculoSalvoResponse,
    CurriculosListagemResponse,
    GerarCartaApresentacaoRequest,
)
from jobsync.perfil_estruturado.domain.montar_curriculo_do_perfil_estruturado_service import (
    MontarCurriculoDoPerfilEstruturado,
)
from jobsync.perfil_estruturado.service_layer.buscar_perfil_estruturado.service import (
    BuscarPerfilEstruturado,
)

router = APIRouter(tags=["currículos"])


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
    salvo = service.executar(body.to_dto())
    location = f"{request.url.path}/{salvo.id}"
    response.headers["Location"] = location
    return CurriculoSalvoResponse.from_dto(salvo)


def _curriculo_pre_montado(
    perfil_identificador: str | None,
    buscar_perfil: BuscarPerfilEstruturado,
) -> Curriculo | None:
    if not perfil_identificador:
        return None
    perfil = buscar_perfil.executar(perfil_identificador)
    if perfil is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Perfil estruturado não encontrado.",
        )
    curriculo = MontarCurriculoDoPerfilEstruturado().executar(perfil)
    if curriculo is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Perfil estruturado não possui conteúdo suficiente.",
        )
    return curriculo


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
) -> CartaApresentacaoResponse:
    """Gera uma carta de apresentação personalizada para a vaga."""
    curriculo_pre_montado = _curriculo_pre_montado(
        body.perfil_identificador, buscar_perfil
    )
    try:
        output = adaptar.executar(
            body.to_dto(curriculo_pre_montado=curriculo_pre_montado)
        )
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
    buscar_perfil: ServiceBuscarPerfilEstruturadoDep,
    download: bool = False,
) -> AdaptarCurriculoResponse | Response:
    """Adapta o currículo à descrição da vaga informada."""
    curriculo_pre_montado = _curriculo_pre_montado(
        body.perfil_identificador, buscar_perfil
    )
    try:
        output = service.executar(
            body.to_dto(curriculo_pre_montado=curriculo_pre_montado)
        )
    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(erro),
        )
    if download:
        return Response(
            content=output.pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{output.nome_arquivo.valor}"'
            },
        )
    return AdaptarCurriculoResponse.from_dto(output)


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
) -> AnalisarAtsResponse:
    """Retorna nota, requisitos faltantes e sugestões de melhoria ATS."""
    curriculo_pre_montado = _curriculo_pre_montado(
        body.perfil_identificador, buscar_perfil
    )
    try:
        output = service.executar(
            body.to_dto(curriculo_pre_montado=curriculo_pre_montado)
        )
    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(erro),
        )
    return AnalisarAtsResponse.from_dto(output)
