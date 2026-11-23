"""Router de domínio de perfil estruturado para a API v1."""

from __future__ import annotations

from dataclasses import replace
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status

from jobsync.entrypoints.api.autorizacao import exigir_perfil_da_requisicao
from jobsync.entrypoints.api.dependencies import (
    ServiceAdicionarConquistaAExperienciaDep,
    ServiceBuscarPerfilEstruturadoDep,
    ServiceImportarPerfilDePdfDep,
    ServiceSalvarPerfilEstruturadoDep,
    ServiceVerificarConquistasParecidasDep,
)
from jobsync.entrypoints.api.schemas.perfil_estruturado import (
    ConquistaAprovadaRequest,
    ConquistasParecidasRequest,
    ConquistasParecidasResponse,
    PerfilEstruturadoRequest,
    PerfilEstruturadoResponse,
    PerfilImportarPdfRequest,
)

from jobsync.perfil_estruturado.domain.exceptions import ExperienciaNaoEncontrada, PerfilEstruturadoNaoEncontrado
from jobsync.perfil_estruturado.service_layer.adicionar_conquista_a_experiencia import (
    AdicionarConquistaAExperienciaInputDto,
)

router = APIRouter(tags=["perfil estruturado"], dependencies=[Depends(exigir_perfil_da_requisicao)])


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


@router.post(
    "/perfil-estruturado/conquistas/parecidas",
    response_model=ConquistasParecidasResponse,
    status_code=status.HTTP_200_OK,
    summary="Verificar conquistas parecidas",
    description=(
        "Compara o texto de uma conquista nova com as conquistas informadas e devolve as parecidas. "
        "Não consulta nem altera o perfil salvo."
    ),
)
def verificar_conquistas_parecidas(
    body: ConquistasParecidasRequest,
    service: ServiceVerificarConquistasParecidasDep,
) -> ConquistasParecidasResponse:
    """Avisa sobre conquistas parecidas antes de o usuário salvar a nova."""
    try:
        parecidas = service.executar(body.to_dto())
    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(erro),
        )
    return ConquistasParecidasResponse(parecidas=list(parecidas))


@router.post(
    "/perfil-estruturado/{perfil_identificador}/experiencias/{experiencia_indice}/conquistas",
    response_model=PerfilEstruturadoResponse,
    status_code=status.HTTP_200_OK,
    summary="Adicionar conquista aprovada a uma experiência",
    description=(
        "Guarda no banco de conquistas da experiência a conquista que o candidato aprovou ao responder "
        "uma pergunta sobre a vaga, com origem RESPOSTA_PERGUNTA. O resto do perfil não muda."
    ),
)
def adicionar_conquista_a_experiencia(
    perfil_identificador: str,
    experiencia_indice: Annotated[int, Path(ge=0, description="Posição da experiência no perfil.")],
    body: ConquistaAprovadaRequest,
    service: ServiceAdicionarConquistaAExperienciaDep,
) -> PerfilEstruturadoResponse:
    """Acrescenta a conquista aprovada à experiência e devolve o perfil atualizado."""
    try:
        perfil = service.executar(
            AdicionarConquistaAExperienciaInputDto(
                perfil_identificador=perfil_identificador,
                experiencia_indice=experiencia_indice,
                texto=body.texto,
            )
        )
    except (PerfilEstruturadoNaoEncontrado, ExperienciaNaoEncontrada) as erro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(erro))
    except ValueError as erro:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(erro))
    return PerfilEstruturadoResponse.from_dto(perfil)
