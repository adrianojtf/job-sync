"""Resultado de domínio para avaliação estruturada de uma descrição de vaga."""
from __future__ import annotations

from dataclasses import dataclass

from jobsync.shared_kernel.domain.score_avaliacao import (
    ResultadoDimensaoAvaliacao,
    calcular_score_geral,
)


@dataclass(frozen=True)
class AvaliacaoDescricaoVaga:
    completude: ResultadoDimensaoAvaliacao
    clareza: ResultadoDimensaoAvaliacao
    relevancia: ResultadoDimensaoAvaliacao
    inclusao: ResultadoDimensaoAvaliacao

    @property
    def score(self) -> int:
        return calcular_score_geral(
            (self.completude, self.clareza, self.relevancia, self.inclusao)
        )
