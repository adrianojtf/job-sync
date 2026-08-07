"""Caso de uso: mover uma candidatura entre colunas do Kanban.

Aceita qualquer transição entre os quatro status (sem máquina de estados
restritiva), conforme decidido em produto.
"""
from __future__ import annotations

from dataclasses import dataclass

from jobsync.candidatura.domain.candidatura import Candidatura, StatusCandidatura
from jobsync.candidatura.domain.candidatura_repository import CandidaturaRepository


@dataclass
class MoverCandidatura:
    """Atualiza o status de uma candidatura, registrando a data da mudança."""

    repositorio_candidatura: CandidaturaRepository

    def executar(self, candidatura_id: str, novo_status: StatusCandidatura) -> Candidatura:
        return self.repositorio_candidatura.atualizar_status(candidatura_id, novo_status)
