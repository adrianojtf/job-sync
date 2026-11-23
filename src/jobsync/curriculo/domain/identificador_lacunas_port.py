"""Porta para identificar as lacunas entre a vaga e o histórico do candidato."""
from __future__ import annotations

from abc import ABC, abstractmethod

from jobsync.curriculo.domain.contexto_vaga import ContextoVaga
from jobsync.curriculo.domain.lacuna_da_vaga import HistoricoDoCandidato, LacunaDaVaga


class IdentificadorLacunasPort(ABC):
    """Contrato para apontar os temas centrais da vaga que o histórico não sustenta."""

    @abstractmethod
    def identificar(
        self, historico: HistoricoDoCandidato, contexto: ContextoVaga
    ) -> tuple[LacunaDaVaga, ...]:
        """Devolve as lacunas ordenadas do tema mais central ao menos central."""
        raise NotImplementedError
