"""Router de domínio de token de captura para a API v1."""

from __future__ import annotations

import logging

from fastapi import APIRouter, status

from jobsync.entrypoints.api.dependencies import ServiceCriarTokenCapturaDep
from jobsync.entrypoints.api.schemas.erro import ProblemaResponse
from jobsync.entrypoints.api.schemas.token_captura import (
    TokenCapturaCriarRequest,
    TokenCapturaResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["tokens de captura"])


@router.post(
    "/tokens-captura",
    response_model=TokenCapturaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Gerar token de captura",
    description=(
        "Gera um novo token opaco para o perfil informado. O token é usado pela "
        "extensão de navegador para registrar vagas capturadas no perfil."
    ),
    responses={status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ProblemaResponse}},
)
def criar_token_captura(
    body: TokenCapturaCriarRequest,
    service: ServiceCriarTokenCapturaDep,
) -> TokenCapturaResponse:
    """Cria um token de captura vinculado ao perfil informado."""
    token = service.executar(body.perfil_identificador)
    logger.info("Token de captura gerado para o perfil %s", token.perfil_identificador)
    return TokenCapturaResponse.from_domain(token)
