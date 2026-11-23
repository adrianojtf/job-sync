"""Modelos de domínio para avaliar textos de experiências profissionais."""
from __future__ import annotations

from dataclasses import dataclass

from jobsync.shared_kernel.domain.score_avaliacao import (
    ResultadoDimensaoAvaliacao,
    calcular_score_geral,
)


@dataclass(frozen=True)
class ExperienciaParaAvaliacao:
    descricao: str
    cargo: str = ""
    empresa: str = ""
    periodo: str = ""
    conquistas: tuple[str, ...] = ()


@dataclass(frozen=True)
class AvaliacaoExperiencia:
    clareza_escrita: ResultadoDimensaoAvaliacao
    qualidade_detalhe: ResultadoDimensaoAvaliacao
    aderencia_vaga: ResultadoDimensaoAvaliacao
    consistencia_textual: ResultadoDimensaoAvaliacao

    @property
    def score(self) -> int:
        return calcular_score_geral(
            (
                self.clareza_escrita,
                self.qualidade_detalhe,
                self.aderencia_vaga,
                self.consistencia_textual,
            )
        )
