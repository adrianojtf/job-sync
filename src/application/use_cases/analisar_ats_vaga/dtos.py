"""DTOs de input/output para o caso de uso AnalisarAtsVaga."""
from __future__ import annotations

from dataclasses import dataclass

from domain.ats_score import ResultadoAtsScore
from domain.curriculo import Curriculo
from domain.vaga import AnaliseVaga


@dataclass(frozen=True)
class AnalisarAtsVagaInputDto:
    """Dados de entrada do caso de uso, vindos da interface (Streamlit).

    Informe `pdf_curriculo` OU `curriculo_pre_montado` — quando este último
    vier preenchido (perfil estruturado, Fase 5), a extração via IA é pulada.
    """

    descricao_vaga: str
    pdf_curriculo: bytes | None = None
    curriculo_pre_montado: Curriculo | None = None


@dataclass(frozen=True)
class AnalisarAtsVagaOutputDto:
    """Resultado do caso de uso: currículo original, análise da vaga, nota e sugestões."""

    curriculo: Curriculo
    analise_vaga: AnaliseVaga
    resultado_ats: ResultadoAtsScore
    sugestoes: tuple[str, ...]
