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
    contexto: str = ""
    responsabilidades: tuple[str, ...] = ()
    skills: tuple[str, ...] = ()

    @property
    def tem_blocos(self) -> bool:
        """Indica se a experiência traz algum dos blocos além da descrição em texto livre."""
        return bool(
            self.contexto.strip() or self.responsabilidades or self.conquistas or self.skills
        )

    @property
    def texto_completo(self) -> str:
        """Descrição e os quatro blocos, um item por linha: o texto que a IA mede ou melhora."""
        linhas = [
            self.descricao.strip(),
            *self.responsabilidades,
            *self.conquistas,
            self.contexto.strip(),
            ", ".join(self.skills),
        ]
        return "\n".join(linha for linha in linhas if linha)


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
