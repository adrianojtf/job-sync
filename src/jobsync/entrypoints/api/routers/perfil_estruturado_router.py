"""Router de domínio de perfil estruturado para a API v1."""

from __future__ import annotations

from dataclasses import replace

from fastapi import APIRouter, HTTPException, status

from jobsync.entrypoints.api.dependencies import (
    ServiceBuscarPerfilEstruturadoDep,
    ServiceImportarPerfilDePdfDep,
    ServiceSalvarPerfilEstruturadoDep,
)
from jobsync.entrypoints.api.schemas.perfil_estruturado import (
    PerfilEstruturadoRequest,
    PerfilEstruturadoResponse,
    PerfilImportarPdfRequest,
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
    try:
        perfil = service.executar(body.to_dto())
    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(erro),
        )
    return PerfilEstruturadoResponse.from_dto(perfil)


@router.put(
    "/perfil-estruturado/{perfil_identificador}",
    response_model=PerfilEstruturadoResponse,
    status_code=status.HTTP_200_OK,
    summary="Atualizar perfil estruturado",
    description="Substitui o perfil estruturado vinculado ao identificador informado.",
)
def atualizar_perfil_estruturado(
    perfil_identificador: str,
    body: PerfilEstruturadoRequest,
    service: ServiceSalvarPerfilEstruturadoDep,
) -> PerfilEstruturadoResponse:
    """Atualiza o perfil estruturado de forma idempotente (PUT)."""
    try:
        input_dto = replace(body.to_dto(), perfil_identificador=perfil_identificador)
        perfil = service.executar(input_dto)
    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(erro),
        )
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


@router.post(
    "/perfil-estruturado/importacoes",
    response_model=PerfilEstruturadoResponse,
    status_code=status.HTTP_200_OK,
    summary="Importar perfil estruturado de PDF",
    description="Extrai um rascunho de perfil estruturado a partir de um PDF.",
)
def importar_perfil_estruturado_de_pdf(
    body: PerfilImportarPdfRequest,
    service: ServiceImportarPerfilDePdfDep,
) -> PerfilEstruturadoResponse:
    """Extrai um rascunho de perfil a partir de um PDF, sem persistir."""
    try:
        dados = service.executar(body.to_dto())
    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(erro),
        )
    return PerfilEstruturadoResponse.from_dto(dados)
