"""Router de domínio de vaga para a API v1."""

from __future__ import annotations

from fastapi import APIRouter, Request, Response, status

from jobsync.entrypoints.api.dependencies import (
    ServiceAvaliarDescricaoVagaDep,
    ServiceCapturarVagaDep,
    ServiceListarVagasCapturadasDep,
)
from jobsync.entrypoints.api.schemas.erro import ProblemaResponse
from jobsync.entrypoints.api.schemas.vaga import (
    AvaliacaoDescricaoVagaResponse,
    AvaliarDescricaoVagaRequest,
    VagaCapturarRequest,
    VagaResponse,
    VagasListagemResponse,
)

router = APIRouter(tags=["vagas"])


@router.post(
    "/vagas/avaliacoes",
    response_model=AvaliacaoDescricaoVagaResponse,
    status_code=status.HTTP_200_OK,
    summary="Avaliar descrição de vaga",
    description=(
        "Avalia completude, clareza, relevância e linguagem inclusiva. "
        "A operação não persiste o texto nem bloqueia outros fluxos."
    ),
    responses={
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": ProblemaResponse,
            "description": "Texto da descrição ausente ou inválido.",
        },
        status.HTTP_502_BAD_GATEWAY: {
            "model": ProblemaResponse,
            "description": "O provedor de avaliação está indisponível.",
        },
    },
)
def avaliar_descricao_vaga(
    body: AvaliarDescricaoVagaRequest,
    service: ServiceAvaliarDescricaoVagaDep,
) -> AvaliacaoDescricaoVagaResponse:
    """Retorna score e categorias estruturadas para uma descrição de vaga."""
    avaliacao = service.executar(body.to_dto())
    return AvaliacaoDescricaoVagaResponse.from_domain(avaliacao)


@router.get(
    "/vagas",
    response_model=VagasListagemResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar vagas",
    description="Lista as vagas capturadas de um perfil ainda não convertidas.",
)
def listar_vagas(
    perfil_identificador: str,
    service: ServiceListarVagasCapturadasDep,
) -> VagasListagemResponse:
    """Retorna as vagas capturadas do perfil informado."""
    vagas = service.executar(perfil_identificador)
    return VagasListagemResponse.from_dto(vagas)


@router.post(
    "/vagas",
    response_model=VagaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Capturar vaga",
    description="Registra uma nova vaga capturada para um perfil.",
)
def capturar_vaga(
    body: VagaCapturarRequest,
    service: ServiceCapturarVagaDep,
    response: Response,
    request: Request,
) -> VagaResponse:
    """Captura uma nova vaga a partir da descrição fornecida."""
    vaga = service.executar(body.to_dto())
    response.headers["Location"] = f"{request.url.path}/{vaga.id}"
    return VagaResponse.from_dto(vaga)
