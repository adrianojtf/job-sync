"""Caso de uso: buscar um currículo adaptado do perfil."""
from __future__ import annotations

from jobsync.curriculo_adaptado.domain.curriculo_adaptado import CurriculoAdaptado
from jobsync.curriculo_adaptado.domain.curriculo_adaptado_repository import (
    CurriculoAdaptadoRepository,
)
from jobsync.curriculo_adaptado.domain.exceptions import CurriculoAdaptadoNaoEncontrado


class BuscarCurriculoAdaptado:
    def __init__(self, repositorio: CurriculoAdaptadoRepository) -> None:
        self._repositorio = repositorio

    def executar(self, curriculo_id: str, perfil_identificador: str) -> CurriculoAdaptado:
        curriculo = self._repositorio.buscar(curriculo_id, perfil_identificador)
        if curriculo is None:
            raise CurriculoAdaptadoNaoEncontrado()
        return curriculo
