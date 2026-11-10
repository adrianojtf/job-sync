"""Router de domínio de candidatura para a API v1."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, Response, status

from jobsync.candidatura import CandidaturaNaoEncontrada, StatusCandidatura
from jobsync.curriculo_salvo.domain.limite_curriculos_salvos import LimiteCurriculosSalvosExcedido
from jobsync.entrypoints.api.dependencies import (
    ServiceConfirmarCandidaturaAjustadaDep,
    ServiceCriarCandidaturaDep,
    ServiceListarCandidaturasDep,
    ServiceMoverCandidaturaDep,
)
from jobsync.entrypoints.api.schemas.candidatura import (
    CandidaturaConfirmarRequest,
    CandidaturaCriarRequest,
    CandidaturaResponse,
    CandidaturasListagemResponse,
    CandidaturaSubmeterRequest,
)
from jobsync.entrypoints.api.schemas.erro import ProblemaResponse

router = APIRouter(tags=["candidaturas"])


@router.get(
    "/candidaturas",
    response_model=CandidaturasListagemResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar candidaturas",
    description="Lista as candidaturas de um perfil agrupadas por status.",
)
def listar_candidaturas(
    perfil_identificador: str,
    service: ServiceListarCandidaturasDep,
) -> CandidaturasListagemResponse:
    """Retorna as candidaturas do perfil agrupadas por status (Kanban)."""
    agrupadas = service.executar(perfil_identificador)
    return CandidaturasListagemResponse.from_dto(agrupadas)


@router.post(
    "/candidaturas",
    response_model=CandidaturaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar candidatura",
    description="Cria uma candidatura a partir de uma vaga e um currículo salvo.",
)
def criar_candidatura(
    body: CandidaturaCriarRequest,
    service: ServiceCriarCandidaturaDep,
    response: Response,
    request: Request,
) -> CandidaturaResponse:
    """Cria uma candidatura com status inicial APLICADO."""
    try:
        candidatura = service.executar(body.to_dto())
    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(erro),
        )
    response.headers["Location"] = f"{request.url.path}/{candidatura.id}"
    return CandidaturaResponse.from_dto(candidatura)


@router.post(
    "/candidaturas-ajustadas",
    response_model=CandidaturaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Confirmar candidatura a partir do currículo ajustado",
    description=(
        "Cria a vaga (já convertida), o currículo salvo com o PDF gerado e a candidatura "
        "com status APLICADO, em uma única operação."
    ),
    responses={
        status.HTTP_409_CONFLICT: {"model": ProblemaResponse},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ProblemaResponse},
    },
)
def confirmar_candidatura_ajustada(
    body: CandidaturaConfirmarRequest,
    service: ServiceConfirmarCandidaturaAjustadaDep,
) -> CandidaturaResponse:
    """Registra a candidatura APLICADO com a vaga e o PDF gerado na tela de ajuste."""
    try:
        candidatura = service.executar(body.to_dto())
    except LimiteCurriculosSalvosExcedido:
        raise
    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(erro),
        )
    return CandidaturaResponse.from_dto(candidatura)


@router.post(
    "/candidaturas/{id}/submissao",
    response_model=CandidaturaResponse,
    status_code=status.HTTP_200_OK,
    summary="Submeter/mover candidatura",
    description=(
        "Atualiza o status de uma candidatura e, opcionalmente, sua posição na coluna de destino. "
        "Sem posição, a candidatura vai para o topo da coluna."
    ),
)
def submeter_candidatura(
    id: str,
    body: CandidaturaSubmeterRequest,
    service: ServiceMoverCandidaturaDep,
) -> CandidaturaResponse:
    """Move a candidatura para o novo status informado."""
    dados = body.to_dto()
    try:
        candidatura = service.executar(id, dados["novo_status"], dados["posicao"])
    except CandidaturaNaoEncontrada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidatura não encontrada.",
        )
    return CandidaturaResponse.from_dto(candidatura)
