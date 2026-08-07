"""Entidades de domínio para vagas descobertas em fontes externas."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum, auto

from jobsync.ats_score import ResultadoAtsScore


class FonteVagaExterna(Enum):
    """Fontes externas de busca de vagas suportadas."""

    REMOTEOK = auto()
    WE_WORK_REMOTELY = auto()
    ARBEITNOW = auto()
    ADZUNA = auto()
    GOOGLE_CUSTOM_SEARCH = auto()


@dataclass(frozen=True)
class VagaExterna:
    """Vaga encontrada em uma fonte externa, antes do cálculo de match."""

    titulo: str
    empresa: str
    descricao: str
    url: str
    fonte: FonteVagaExterna
    descricao_incompleta: bool = False
    data_publicacao: date | None = None

    def __post_init__(self) -> None:
        if not self.titulo or not self.titulo.strip():
            raise ValueError("O título da vaga externa não pode ser vazio.")
        if not self.empresa or not self.empresa.strip():
            raise ValueError("A empresa da vaga externa não pode ser vazia.")
        if not self.descricao or not self.descricao.strip():
            raise ValueError("A descrição da vaga externa não pode ser vazia.")
        if not self.url or not self.url.strip():
            raise ValueError("A URL da vaga externa não pode ser vazia.")


@dataclass(frozen=True)
class VagaComScore:
    """Vaga externa já com o resultado do cálculo de ATS Score."""

    vaga: VagaExterna
    resultado_score: ResultadoAtsScore
