"""Resolução do currículo pré-montado a partir do perfil estruturado, comum aos routers."""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import HTTPException, status

from jobsync.curriculo import Curriculo, ExperienciaParaAvaliacao
from jobsync.curriculo_adaptado.domain.exceptions import CurriculoAdaptadoNaoEncontrado
from jobsync.curriculo_adaptado.service_layer.buscar_curriculo_adaptado import (
    BuscarCurriculoAdaptado,
)
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


def experiencias_do_perfil(
    perfil: PerfilEstruturado | None,
) -> tuple[ExperienciaParaAvaliacao, ...] | None:
    if perfil is None or not perfil.experiencias:
        return None
    return tuple(
        ExperienciaParaAvaliacao(
            cargo=experiencia.cargo,
            empresa=experiencia.empresa,
            periodo=experiencia.periodo,
            descricao=experiencia.descricao,
            conquistas=tuple(conquista.texto for conquista in experiencia.conquistas),
        )
        for experiencia in perfil.experiencias
    )


@dataclass(frozen=True)
class FonteDoCurriculo:
    """Currículo de partida já montado (None quando a fonte é um PDF) e as experiências a reescrever."""

    curriculo: Curriculo | None
    experiencias: tuple[ExperienciaParaAvaliacao, ...] | None


def resolver_fonte_do_curriculo(
    perfil_identificador: str | None,
    curriculo_adaptado_id: str | None,
    pdf_base64: str | None,
    buscar_perfil: BuscarPerfilEstruturado,
    buscar_adaptado: BuscarCurriculoAdaptado,
) -> FonteDoCurriculo:
    """Escolhe a fonte do pedido: um currículo adaptado salvo ou o perfil estruturado (ou o PDF)."""
    if not curriculo_adaptado_id:
        perfil = buscar_perfil_estruturado(perfil_identificador, buscar_perfil)
        return FonteDoCurriculo(montar_curriculo_pre_montado(perfil), experiencias_do_perfil(perfil))
    if pdf_base64:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Informe só uma fonte: curriculo_adaptado_id ou pdf_base64.",
        )
    if not perfil_identificador:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Informe perfil_identificador junto com curriculo_adaptado_id.",
        )
    try:
        adaptado = buscar_adaptado.executar(curriculo_adaptado_id, perfil_identificador)
    except CurriculoAdaptadoNaoEncontrado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Currículo adaptado não encontrado."
        )
    return FonteDoCurriculo(adaptado.como_curriculo_base(), adaptado.experiencias_para_adaptacao())
