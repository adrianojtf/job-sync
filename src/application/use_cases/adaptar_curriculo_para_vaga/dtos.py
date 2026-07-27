"""DTOs de input/output para o caso de uso AdaptarCurriculoParaVaga."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from domain.curriculo import Curriculo
from domain.nome_arquivo import NomeArquivo


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
    """Resultado do caso de uso: PDF gerado e nome de arquivo padronizado."""

    pdf_bytes: bytes
    nome_arquivo: NomeArquivo
    curriculo_adaptado: Curriculo
