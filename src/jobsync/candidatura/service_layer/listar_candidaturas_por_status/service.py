"""Caso de uso: listar as candidaturas de um perfil agrupadas por status (Kanban)."""
from __future__ import annotations

from dataclasses import dataclass

from jobsync.candidatura.domain.candidatura import Candidatura, StatusCandidatura
from jobsync.candidatura.domain.candidatura_repository import CandidaturaRepository


@dataclass
class ListarCandidaturasPorStatus:
    """Agrupa as candidaturas do perfil por status, incluindo colunas vazias."""

    repositorio_candidatura: CandidaturaRepository

    def executar(self, perfil_identificador: str) -> dict[StatusCandidatura, tuple[Candidatura, ...]]:
        candidaturas = self.repositorio_candidatura.listar_por_perfil(perfil_identificador)

        agrupadas: dict[StatusCandidatura, tuple[Candidatura, ...]] = {
            status: () for status in StatusCandidatura
        }
        for candidatura in candidaturas:
            agrupadas[candidatura.status] = agrupadas[candidatura.status] + (candidatura,)

        return agrupadas
