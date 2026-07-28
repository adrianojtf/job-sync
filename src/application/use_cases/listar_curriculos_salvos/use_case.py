"""Caso de uso: listar os currículos salvos de um perfil."""
from __future__ import annotations

from domain.curriculo_salvo import CurriculoSalvo
from domain.curriculo_salvo.curriculo_salvo_repository import CurriculoSalvoRepository


class ListarCurriculosSalvos:
    """Lista os currículos salvos de um perfil, mais recentes primeiro."""

    def __init__(self, repositorio_curriculo_salvo: CurriculoSalvoRepository) -> None:
        self._repositorio_curriculo_salvo = repositorio_curriculo_salvo

    def executar(self, perfil_identificador: str) -> tuple[CurriculoSalvo, ...]:
        return self._repositorio_curriculo_salvo.listar_por_perfil(perfil_identificador)
