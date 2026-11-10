"""Router de domínio de perfil para a API v1."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from jobsync.entrypoints.api.autorizacao import exigir_acesso_ao_perfil, exigir_perfil_da_requisicao
from jobsync.entrypoints.api.dependencies import UsuarioAutenticadoDep
from jobsync.entrypoints.api.schemas.perfil import (
    PerfilResponse,
    PerfisListagemResponse,
)

router = APIRouter(tags=["perfis"], dependencies=[Depends(exigir_perfil_da_requisicao)])


@router.get(
    "/perfis",
    response_model=PerfisListagemResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar perfis",
    description="Placeholder: retorna uma lista vazia de perfis.",
)
def listar_perfis() -> PerfisListagemResponse:
    """Retorna a listagem de perfis (placeholder)."""
    return PerfisListagemResponse(items=[], total=0)


@router.get(
    "/perfis/{id}",
    response_model=PerfilResponse,
    status_code=status.HTTP_200_OK,
    summary="Obter o próprio perfil",
    description=(
        "Devolve o perfil do usuário autenticado. Não cria perfis: eles nascem no cadastro "
        "ou no primeiro login. Pedir o perfil de outra pessoa responde 403."
    ),
)
def obter_perfil(id: str, usuario: UsuarioAutenticadoDep) -> PerfilResponse:
    """Confirma que o perfil pedido é o da sessão e o devolve."""
    exigir_acesso_ao_perfil(id, usuario)
    return PerfilResponse(identificador=usuario.perfil_identificador)
