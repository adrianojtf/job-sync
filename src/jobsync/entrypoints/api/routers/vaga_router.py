"""Router de domínio de vaga para a API v1."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response, status

from jobsync.entrypoints.api.autorizacao import exigir_perfil_da_requisicao
from jobsync.entrypoints.api.dependencies import (
    ServiceAvaliarDescricaoVagaDep,
    ServiceCapturarVagaDep,
    ServiceExtrairDadosVagaDep,
    ServiceListarVagasCapturadasDep,
    UsuarioAutenticadoDep,
)
from jobsync.entrypoints.api.schemas.erro import ProblemaResponse
from jobsync.entrypoints.api.schemas.vaga import (
    AvaliacaoDescricaoVagaResponse,
    AvaliarDescricaoVagaRequest,
    DadosVagaResponse,
    ExtracaoVagaRequest,
    VagaCapturarRequest,
    VagaResponse,
    VagasListagemResponse,
)

router = APIRouter(tags=["vagas"], dependencies=[Depends(exigir_perfil_da_requisicao)])


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


@router.post(
    "/vagas/extracoes",
    response_model=DadosVagaResponse,
    status_code=status.HTTP_200_OK,
    summary="Extrair dados de vaga",
    description=(
        "Lê cargo, empresa, local e descrição de uma vaga a partir do link ou do texto e devolve "
        "um rascunho para revisão. Nada é salvo. Quando link e texto são informados juntos, o texto "
        "tem prioridade. Se o link não puder ser lido, a resposta orienta a colar o texto da vaga."
    ),
    responses={
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": ProblemaResponse,
            "description": "Link inválido, fonte não suportada ou nenhum dado informado.",
        },
        status.HTTP_429_TOO_MANY_REQUESTS: {
            "model": ProblemaResponse,
            "description": "Limite de leituras atingido; veja o cabeçalho `Retry-After`.",
        },
        status.HTTP_502_BAD_GATEWAY: {
            "model": ProblemaResponse,
            "description": "O site da vaga bloqueou a leitura, a vaga não existe ou não foi possível acessá-la.",
        },
    },
)
def extrair_dados_vaga(
    body: ExtracaoVagaRequest,
    service: ServiceExtrairDadosVagaDep,
    usuario: UsuarioAutenticadoDep,
) -> DadosVagaResponse:
    """Devolve o rascunho dos dados da vaga lida do link ou do texto."""
    dados = service.executar(body.to_dto(usuario_id=usuario.perfil_identificador))
    return DadosVagaResponse.from_domain(dados)
