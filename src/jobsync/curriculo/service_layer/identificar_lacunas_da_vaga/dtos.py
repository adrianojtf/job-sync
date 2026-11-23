"""DTO de input para o caso de uso IdentificarLacunasDaVaga."""
from __future__ import annotations

from dataclasses import dataclass

from jobsync.curriculo.domain.contexto_vaga import ContextoVaga
from jobsync.curriculo.domain.lacuna_da_vaga import HistoricoDoCandidato


@dataclass(frozen=True)
class IdentificarLacunasDaVagaInputDto:
    """O histórico do candidato e o contexto da vaga a comparar."""

    historico: HistoricoDoCandidato
    contexto: ContextoVaga
