"""Router de domínio de vaga externa para a API v1."""

from __future__ import annotations

from fastapi import APIRouter, status

from jobsync.entrypoints.api.dependencies import ServiceDescobrirVagasComMatchDep
from jobsync.entrypoints.api.schemas.vaga_externa import (
    DescobrirVagasRequest,
    DescobrirVagasResponse,
)

router = APIRouter(tags=["vagas externas"])


@router.post(
    "/vagas/descobrir",
    response_model=DescobrirVagasResponse,
    status_code=status.HTTP_200_OK,
    summary="Descobrir vagas externas",
    description="Busca vagas em fontes externas e calcula o match com um currículo.",
)
def descobrir_vagas(
    body: DescobrirVagasRequest,
    service: ServiceDescobrirVagasComMatchDep,
) -> DescobrirVagasResponse:
    """Descobre vagas externas ordenadas por score de compatibilidade."""
    input_dto = body.to_dto()
    vagas = service.executar(
        termo=input_dto["termo"],
        pdf_curriculo=input_dto["pdf_curriculo"],
        dias_maximo=input_dto["dias_maximo"],
    )
    return DescobrirVagasResponse.from_dto(vagas)
