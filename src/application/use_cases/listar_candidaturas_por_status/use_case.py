"""Caso de uso: listar as candidaturas de um perfil agrupadas por status (Kanban)."""
from __future__ import annotations

from domain.candidatura import Candidatura, StatusCandidatura
from domain.candidatura.candidatura_repository import CandidaturaRepository


class ListarCandidaturasPorStatus:
    """Agrupa as candidaturas do perfil por status, incluindo colunas vazias."""

    def __init__(self, repositorio_candidatura: CandidaturaRepository) -> None:
        self._repositorio_candidatura = repositorio_candidatura

    def executar(self, perfil_identificador: str) -> dict[StatusCandidatura, tuple[Candidatura, ...]]:
        candidaturas = self._repositorio_candidatura.listar_por_perfil(perfil_identificador)

        agrupadas: dict[StatusCandidatura, tuple[Candidatura, ...]] = {
            status: () for status in StatusCandidatura
        }
        for candidatura in candidaturas:
            agrupadas[candidatura.status] = agrupadas[candidatura.status] + (candidatura,)

        return agrupadas
