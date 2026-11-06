"""Schemas compartilhados para dimensões de avaliação."""
from __future__ import annotations

from pydantic import BaseModel, Field

from jobsync.shared_kernel.domain import ResultadoDimensaoAvaliacao


class ResultadoDimensaoAvaliacaoResponse(BaseModel):
    """Score, nível categórico e confiança de uma dimensão."""

    score: int = Field(
        ge=0,
        le=100,
        description="Score normalizado desta dimensão, entre 0 e 100.",
        examples=[75],
    )
    nivel: str = Field(
        description="Categoria fixa associada à maior probabilidade do Jev.",
        examples=["adequado"],
    )
    confianca: float = Field(
        ge=0,
        le=1,
        description="Confiança do Jev nesta avaliação, entre 0 e 1.",
        examples=[0.82],
    )

    @classmethod
    def from_domain(
        cls,
        resultado: ResultadoDimensaoAvaliacao,
    ) -> "ResultadoDimensaoAvaliacaoResponse":
        return cls(
            score=resultado.score,
            nivel=resultado.nivel,
            confianca=resultado.confianca,
        )
