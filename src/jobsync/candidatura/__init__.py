"""Domínio Candidatura: gestão de candidaturas no Kanban."""

from jobsync.candidatura.domain.candidatura import (
    Candidatura,
    MudancaStatus,
    StatusCandidatura,
)
from jobsync.candidatura.domain.candidatura_repository import (
    CandidaturaNaoEncontrada,
    CandidaturaRepository,
)

__all__ = [
    "Candidatura",
    "CandidaturaNaoEncontrada",
    "CandidaturaRepository",
    "MudancaStatus",
    "StatusCandidatura",
]
