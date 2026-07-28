"""DTOs de input/output para o caso de uso AdaptarCurriculoParaVaga."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from domain.curriculo import Curriculo
from domain.nome_arquivo import NomeArquivo
from domain.vaga import AnaliseVaga


@dataclass(frozen=True)
class AdaptarCurriculoParaVagaInputDto:
    """Dados de entrada do caso de uso, vindos da interface (Streamlit)."""

    pdf_curriculo: bytes
    descricao_vaga: str
    idioma_alvo: str
    cargo_alvo: str
    empresa_alvo: str
    data_referencia: date | None = None


@dataclass(frozen=True)
class AdaptarCurriculoParaVagaOutputDto:
    """Resultado do caso de uso: PDF gerado e nome de arquivo padronizado.

    Expõe `analise_vaga` (já calculada internamente) para que outras
    funcionalidades (ATS Score, carta de apresentação) possam reaproveitá-la
    sem uma segunda chamada de IA para analisar a mesma vaga.
    """

    pdf_bytes: bytes
    nome_arquivo: NomeArquivo
    curriculo_adaptado: Curriculo
    analise_vaga: AnaliseVaga
