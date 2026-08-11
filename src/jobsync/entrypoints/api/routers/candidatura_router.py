"""Router de domínio de candidatura para a API v1."""

from __future__ import annotations

from fastapi import APIRouter, Request, Response, status

from jobsync.candidatura import StatusCandidatura
from jobsync.entrypoints.api.dependencies import (
    ServiceCriarCandidaturaDep,
    ServiceListarCandidaturasDep,
    ServiceMoverCandidaturaDep,
)
from jobsync.entrypoints.api.schemas.candidatura import (
    CandidaturaCriarRequest,
    CandidaturaResponse,
    CandidaturasListagemResponse,
    CandidaturaSubmeterRequest,
)

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
    candidatura = service.executar(body.to_dto())
    response.headers["Location"] = f"{request.url.path}/{candidatura.id}"
    return CandidaturaResponse.from_dto(candidatura)


@router.post(
    "/candidaturas/{id}/submissao",
    response_model=CandidaturaResponse,
    status_code=status.HTTP_200_OK,
    summary="Submeter/mover candidatura",
    description="Atualiza o status de uma candidatura.",
)
def submeter_candidatura(
    id: str,
    body: CandidaturaSubmeterRequest,
    service: ServiceMoverCandidaturaDep,
) -> CandidaturaResponse:
    """Move a candidatura para o novo status informado."""
    novo_status = body.to_dto()["novo_status"]
    candidatura = service.executar(id, novo_status)
    return CandidaturaResponse.from_dto(candidatura)
