"""Rotas do currículo adaptado: salvar ao confirmar a revisão, listar, abrir e editar (JOB-0041)."""
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from jobsync.curriculo_adaptado.domain.exceptions import CurriculoAdaptadoNaoEncontrado
from jobsync.entrypoints.api.autorizacao import exigir_perfil_da_requisicao
from jobsync.entrypoints.api.dependencies import (
    ServiceAtualizarCurriculoAdaptadoDep,
    ServiceBuscarCurriculoAdaptadoDep,
    ServiceListarCurriculosAdaptadosDep,
    ServiceSalvarCurriculoAdaptadoDep,
)
from jobsync.entrypoints.api.schemas.curriculo_adaptado import (
    CurriculoAdaptadoAtualizarRequest,
    CurriculoAdaptadoPdfResponse,
    CurriculoAdaptadoResponse,
    CurriculoAdaptadoSalvarRequest,
    CurriculosAdaptadosListagemResponse,
)
from jobsync.entrypoints.api.schemas.erro import ProblemaResponse

router = APIRouter(
    prefix="/curriculos-adaptados",
    tags=["currículos adaptados"],
    dependencies=[Depends(exigir_perfil_da_requisicao)],
)

_NAO_ENCONTRADO = {
    status.HTTP_404_NOT_FOUND: {
        "model": ProblemaResponse,
        "description": "Currículo adaptado inexistente ou de outro perfil.",
    },
}
_INVALIDO = {
    status.HTTP_422_UNPROCESSABLE_ENTITY: {
        "model": ProblemaResponse,
        "description": "Rascunho ou dados da vaga inválidos.",
    },
}


def _nao_encontrado() -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Currículo adaptado não encontrado.")


def _invalido(erro: ValueError) -> HTTPException:
    return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(erro))


@router.post(
    "",
    response_model=CurriculoAdaptadoPdfResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Salvar currículo adaptado",
    description=(
        "Guarda o currículo adaptado confirmado na revisão, com a vaga usada, e devolve o PDF "
        "gerado a partir dele. Substitui a geração de PDF sem persistência da tela de ajuste."
    ),
    responses=_INVALIDO,
)
def salvar_curriculo_adaptado(
    body: CurriculoAdaptadoSalvarRequest,
    service: ServiceSalvarCurriculoAdaptadoDep,
    response: Response,
    request: Request,
) -> CurriculoAdaptadoPdfResponse:
    try:
        resultado = service.executar(body.to_dto())
    except ValueError as erro:
        raise _invalido(erro)
    response.headers["Location"] = f"{request.url.path}/{resultado.curriculo.id}"
    return CurriculoAdaptadoPdfResponse.from_dto(resultado)


@router.get(
    "",
    response_model=CurriculosAdaptadosListagemResponse,
    summary="Listar currículos adaptados",
    description="Lista os currículos adaptados do perfil, do editado mais recentemente ao mais antigo.",
)
def listar_curriculos_adaptados(
    perfil_identificador: str,
    service: ServiceListarCurriculosAdaptadosDep,
) -> CurriculosAdaptadosListagemResponse:
    return CurriculosAdaptadosListagemResponse.from_domain(service.executar(perfil_identificador))


@router.get(
    "/{id}",
    response_model=CurriculoAdaptadoResponse,
    summary="Abrir currículo adaptado",
    description="Devolve o conteúdo salvo e a vaga usada, para reabrir a revisão.",
    responses=_NAO_ENCONTRADO,
)
def obter_curriculo_adaptado(
    id: str,
    perfil_identificador: str,
    service: ServiceBuscarCurriculoAdaptadoDep,
) -> CurriculoAdaptadoResponse:
    try:
        return CurriculoAdaptadoResponse.from_domain(service.executar(id, perfil_identificador))
    except CurriculoAdaptadoNaoEncontrado:
        raise _nao_encontrado()


@router.put(
    "/{id}",
    response_model=CurriculoAdaptadoPdfResponse,
    summary="Salvar a edição do currículo adaptado",
    description="Substitui o conteúdo salvo e devolve o PDF regenerado a partir dele.",
    responses={**_NAO_ENCONTRADO, **_INVALIDO},
)
def atualizar_curriculo_adaptado(
    id: str,
    body: CurriculoAdaptadoAtualizarRequest,
    service: ServiceAtualizarCurriculoAdaptadoDep,
) -> CurriculoAdaptadoPdfResponse:
    try:
        resultado = service.executar(body.to_dto(id))
    except CurriculoAdaptadoNaoEncontrado:
        raise _nao_encontrado()
    except ValueError as erro:
        raise _invalido(erro)
    return CurriculoAdaptadoPdfResponse.from_dto(resultado)
