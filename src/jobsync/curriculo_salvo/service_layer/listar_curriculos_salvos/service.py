"""Caso de uso: listar os currículos salvos de um perfil."""
from __future__ import annotations

from dataclasses import dataclass

from jobsync.curriculo_salvo.domain.curriculo_salvo import CurriculoSalvo
from jobsync.curriculo_salvo.domain.curriculo_salvo_repository import CurriculoSalvoRepository


@dataclass
class ListarCurriculosSalvos:
    """Lista os currículos salvos de um perfil, mais recentes primeiro."""

    _repositorio_curriculo_salvo: CurriculoSalvoRepository

    def executar(self, perfil_identificador: str) -> tuple[CurriculoSalvo, ...]:
        return self._repositorio_curriculo_salvo.listar_por_perfil(perfil_identificador)
