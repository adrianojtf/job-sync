"""DTOs de input/output para o caso de uso AnalisarAtsVaga."""
from __future__ import annotations

from dataclasses import dataclass

from domain.ats_score import ResultadoAtsScore
from domain.curriculo import Curriculo
from domain.vaga import AnaliseVaga


@dataclass(frozen=True)
class AnalisarAtsVagaInputDto:
    """Dados de entrada do caso de uso, vindos da interface (Streamlit)."""

    pdf_curriculo: bytes
    descricao_vaga: str


@dataclass(frozen=True)
class AnalisarAtsVagaOutputDto:
    """Resultado do caso de uso: currículo original, análise da vaga, nota e sugestões."""

    curriculo: Curriculo
    analise_vaga: AnaliseVaga
    resultado_ats: ResultadoAtsScore
    sugestoes: tuple[str, ...]
