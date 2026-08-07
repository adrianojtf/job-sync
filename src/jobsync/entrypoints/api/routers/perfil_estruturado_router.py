"""Router de domínio de perfil estruturado para a API v1."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from jobsync.entrypoints.api.dependencies import (
    ServiceBuscarPerfilEstruturadoDep,
    ServiceSalvarPerfilEstruturadoDep,
)
from jobsync.entrypoints.api.schemas.perfil_estruturado import (
    PerfilEstruturadoRequest,
    PerfilEstruturadoResponse,
)

router = APIRouter(tags=["perfil estruturado"])


@router.post(
    "/perfil-estruturado",
    response_model=PerfilEstruturadoResponse,
    status_code=status.HTTP_200_OK,
    summary="Salvar ou atualizar perfil estruturado",
    description="Cria ou substitui o perfil estruturado vinculado ao identificador informado.",
)
def salvar_perfil_estruturado(
    body: PerfilEstruturadoRequest,
    service: ServiceSalvarPerfilEstruturadoDep,
) -> PerfilEstruturadoResponse:
    """Persiste os dados estruturados do perfil (upsert)."""
    perfil = service.executar(body.to_dto())
    return PerfilEstruturadoResponse.from_dto(perfil)


@router.get(
    "/perfil-estruturado/{perfil_identificador}",
    response_model=PerfilEstruturadoResponse,
    status_code=status.HTTP_200_OK,
    summary="Buscar perfil estruturado",
    description="Busca o perfil estruturado pelo identificador.",
)
def buscar_perfil_estruturado(
    perfil_identificador: str,
    service: ServiceBuscarPerfilEstruturadoDep,
) -> PerfilEstruturadoResponse:
    """Retorna o perfil estruturado existente, ou 404 caso não encontrado."""
    perfil = service.executar(perfil_identificador)
    if perfil is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil estruturado nao encontrado",
        )
    return PerfilEstruturadoResponse.from_dto(perfil)
