"""Caso de uso: listar os currículos adaptados de um perfil, do atualizado mais recente ao mais antigo."""
from __future__ import annotations

from jobsync.curriculo_adaptado.domain.curriculo_adaptado import CurriculoAdaptado
from jobsync.curriculo_adaptado.domain.curriculo_adaptado_repository import (
    CurriculoAdaptadoRepository,
)


class ListarCurriculosAdaptados:
    def __init__(self, repositorio: CurriculoAdaptadoRepository) -> None:
        self._repositorio = repositorio

    def executar(self, perfil_identificador: str) -> tuple[CurriculoAdaptado, ...]:
        return self._repositorio.listar_por_perfil(perfil_identificador)
