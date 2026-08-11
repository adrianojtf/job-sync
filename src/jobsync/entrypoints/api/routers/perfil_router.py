"""Router de domínio de perfil para a API v1."""

from __future__ import annotations

from fastapi import APIRouter, status

from jobsync.entrypoints.api.dependencies import ServiceEntrarOuCriarPerfilDep
from jobsync.entrypoints.api.schemas.perfil import (
    PerfilResponse,
    PerfisListagemResponse,
)

router = APIRouter(tags=["perfis"])


@router.get(
    "/perfis",
    response_model=PerfisListagemResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar perfis",
    description="Placeholder: retorna uma lista vazia de perfis.",
)
def listar_perfis() -> PerfisListagemResponse:
    """Retorna a listagem de perfis (placeholder)."""
    return PerfisListagemResponse(items=[], total=0)


@router.get(
    "/perfis/{id}",
    response_model=PerfilResponse,
    status_code=status.HTTP_200_OK,
    summary="Obter ou criar perfil",
    description="Busca o perfil pelo identificador, criando-o se necessário.",
)
def obter_perfil(id: str, service: ServiceEntrarOuCriarPerfilDep) -> PerfilResponse:
    """Resolve o perfil ativo a partir do identificador."""
    perfil = service.executar(id)
    return PerfilResponse.from_dto(perfil)
