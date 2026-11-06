"""Resolução do currículo pré-montado a partir do perfil estruturado, comum aos routers."""

from __future__ import annotations

from fastapi import HTTPException, status

from jobsync.curriculo import Curriculo
from jobsync.perfil_estruturado.domain.montar_curriculo_do_perfil_estruturado_service import (
    MontarCurriculoDoPerfilEstruturado,
)
from jobsync.perfil_estruturado.domain.perfil_estruturado import PerfilEstruturado
from jobsync.perfil_estruturado.service_layer.buscar_perfil_estruturado.service import (
    BuscarPerfilEstruturado,
)


def buscar_perfil_estruturado(
    perfil_identificador: str | None,
    buscar_perfil: BuscarPerfilEstruturado,
) -> PerfilEstruturado | None:
    """Retorna o perfil informado, None sem identificador, ou 422 se ele não existir."""
    if not perfil_identificador:
        return None
    perfil = buscar_perfil.executar(perfil_identificador)
    if perfil is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Perfil estruturado não encontrado.",
        )
    return perfil


def montar_curriculo_pre_montado(perfil: PerfilEstruturado | None) -> Curriculo | None:
    """Monta o currículo do perfil, ou 422 se o perfil não tiver conteúdo suficiente."""
    if perfil is None:
        return None
    curriculo = MontarCurriculoDoPerfilEstruturado().executar(perfil)
    if curriculo is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Perfil estruturado não possui conteúdo suficiente.",
        )
    return curriculo
