"""Caso de uso: mover uma candidatura entre colunas do Kanban.

Aceita qualquer transição entre os quatro status (sem máquina de estados
restritiva), conforme decidido em produto.
"""
from __future__ import annotations

from domain.candidatura import Candidatura, StatusCandidatura
from domain.candidatura.candidatura_repository import CandidaturaRepository


class MoverCandidatura:
    """Atualiza o status de uma candidatura, registrando a data da mudança."""

    def __init__(self, repositorio_candidatura: CandidaturaRepository) -> None:
        self._repositorio_candidatura = repositorio_candidatura

    def executar(self, candidatura_id: str, novo_status: StatusCandidatura) -> Candidatura:
        return self._repositorio_candidatura.atualizar_status(candidatura_id, novo_status)
