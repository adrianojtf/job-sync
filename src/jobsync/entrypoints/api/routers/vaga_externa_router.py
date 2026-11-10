"""Router de domínio de vaga externa para a API v1."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from jobsync.entrypoints.api.autorizacao import exigir_perfil_da_requisicao
from jobsync.entrypoints.api.curriculo_pre_montado import (
    buscar_perfil_estruturado,
    montar_curriculo_pre_montado,
)
from jobsync.entrypoints.api.dependencies import (
    ServiceBuscarPerfilEstruturadoDep,
    ServiceCandidatarNaVagaExternaDep,
    ServiceDescobrirVagasComMatchDep,
)
from jobsync.entrypoints.api.schemas.erro import ProblemaResponse
from jobsync.entrypoints.api.schemas.vaga_externa import (
    CandidatarVagaExternaRequest,
    CandidatarVagaExternaResponse,
    DescobrirVagasRequest,
    DescobrirVagasResponse,
)

router = APIRouter(tags=["vagas externas"], dependencies=[Depends(exigir_perfil_da_requisicao)])


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


@router.post(
    "/vagas/descobertas/candidaturas",
    response_model=CandidatarVagaExternaResponse,
    status_code=status.HTTP_200_OK,
    summary="Candidatar em vaga externa",
    description=(
        "Gera o currículo adaptado, a nota ATS e a carta de apresentação para uma vaga "
        "descoberta. Não preenche formulários de terceiros: o cliente abre `url_vaga` "
        "para o candidato aplicar."
    ),
    responses={
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": ProblemaResponse,
            "description": "Dados inválidos, sem fonte de currículo ou perfil estruturado inexistente.",
        },
    },
)
def candidatar_na_vaga_externa(
    body: CandidatarVagaExternaRequest,
    service: ServiceCandidatarNaVagaExternaDep,
    buscar_perfil: ServiceBuscarPerfilEstruturadoDep,
) -> CandidatarVagaExternaResponse:
    """Prepara os artefatos de candidatura para a vaga externa informada."""
    perfil = buscar_perfil_estruturado(body.perfil_identificador, buscar_perfil)
    curriculo_pre_montado = montar_curriculo_pre_montado(perfil)
    try:
        output = service.executar(body.to_dto(curriculo_pre_montado=curriculo_pre_montado))
    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(erro),
        )
    return CandidatarVagaExternaResponse.from_dto(output)
