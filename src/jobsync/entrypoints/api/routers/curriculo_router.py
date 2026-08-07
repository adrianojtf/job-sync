"""Router de domínio de currículo para a API v1."""

from __future__ import annotations

from datetime import datetime
from fastapi import APIRouter, Request, Response, status

from jobsync.curriculo_salvo import CurriculoSalvo
from jobsync.curriculo_salvo.service_layer.salvar_curriculo import SalvarCurriculo
from jobsync.entrypoints.api.dependencies import (
    ServiceAdaptarCurriculoDep,
    ServiceAnalisarAtsVagaDep,
    ServiceSalvarCurriculoDep,
)
from jobsync.entrypoints.api.schemas.curriculo import (
    AdaptarCurriculoRequest,
    AdaptarCurriculoResponse,
    AnalisarAtsRequest,
    AnalisarAtsResponse,
    CurriculoSalvarRequest,
    CurriculoSalvoResponse,
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


@router.get(
    "/curriculos/{id}",
    response_model=CurriculoSalvoResponse,
    status_code=status.HTTP_200_OK,
    summary="Obter currículo",
    description="Placeholder: retorna um currículo pelo identificador.",
)
def obter_curriculo(id: str) -> CurriculoSalvo:
    """Retorna um currículo salvo pelo identificador (placeholder)."""
    return CurriculoSalvo(
        id=id,
        perfil_identificador="placeholder",
        nome_referencia="placeholder",
        pdf_bytes=b"placeholder",
        data_upload=datetime.now(),
    )


@router.post(
    "/curriculos/{id}/adaptacoes",
    response_model=AdaptarCurriculoResponse,
    status_code=status.HTTP_200_OK,
    summary="Adaptar currículo para vaga",
    description="Gera um currículo adaptado a uma vaga específica.",
)
def adaptar_curriculo(
    id: str,
    body: AdaptarCurriculoRequest,
    service: ServiceAdaptarCurriculoDep,
) -> AdaptarCurriculoResponse:
    """Adapta o currículo PDF à descrição da vaga informada."""
    output = service.executar(body.to_dto())
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
) -> AnalisarAtsResponse:
    """Retorna nota, requisitos faltantes e sugestões de melhoria ATS."""
    output = service.executar(body.to_dto())
    return AnalisarAtsResponse.from_dto(output)
