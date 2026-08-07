"""Porta para busca de vagas em fontes externas."""
from __future__ import annotations

from abc import ABC, abstractmethod

from jobsync.vaga_externa.domain.vaga_externa import VagaExterna


class BuscadorVagasExternoPort(ABC):
    """Interface única implementada por cada adapter de fonte externa de vagas."""

    @abstractmethod
    def buscar(self, termo: str, dias_maximo: int | None = None) -> tuple[VagaExterna, ...]:
        """Busca vagas pelo termo informado, opcionalmente restrito a publicações recentes.

        `dias_maximo` é um hint best-effort: só a Adzuna o usa nativamente na
        chamada HTTP (`max_days_old`); as demais fontes o ignoram e retornam
        `data_publicacao` (quando disponível) para filtro posterior pelo use
        case orquestrador.

        Implementações devem tratar erros de rede/timeout internamente e
        retornar uma tupla vazia em caso de falha, nunca propagar exceção
        não tratada ao use case orquestrador.
        """
        raise NotImplementedError
