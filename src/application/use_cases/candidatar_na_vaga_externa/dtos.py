"""DTOs de input/output para o caso de uso CandidatarNaVagaExterna."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from domain.ats_score import ResultadoAtsScore
from domain.nome_arquivo import NomeArquivo
from domain.vaga_externa import VagaExterna


@dataclass(frozen=True)
class CandidatarNaVagaExternaInputDto:
    """Dados de entrada do caso de uso, vindos da interface (Streamlit)."""

    pdf_curriculo: bytes
    vaga: VagaExterna
    idioma_alvo: str
    cargo_alvo: str
    empresa_alvo: str
    data_referencia: date | None = None


@dataclass(frozen=True)
class CandidatarNaVagaExternaOutputDto:
    """Resultado do caso de uso: artefatos prontos para a candidatura em um clique.

    `url_vaga` é repassada sem alteração a partir do input — a UI usa esse
    valor para abrir a vaga original em nova aba (sem autofill de formulário).
    """

    pdf_bytes: bytes
    nome_arquivo: NomeArquivo
    resultado_ats: ResultadoAtsScore
    carta_apresentacao: str
    url_vaga: str
