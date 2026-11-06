"""DTOs de input/output para o caso de uso GerarPdfCurriculoRevisado."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from jobsync.curriculo import RascunhoCurriculoAdaptado
from jobsync.shared_kernel.domain import NomeArquivo


@dataclass(frozen=True)
class GerarPdfCurriculoRevisadoInputDto:
    """Rascunho confirmado pelo usuário e dados da vaga-alvo."""

    rascunho: RascunhoCurriculoAdaptado
    idioma_alvo: str
    cargo_alvo: str
    empresa_alvo: str
    data_referencia: date | None = None


@dataclass(frozen=True)
class GerarPdfCurriculoRevisadoOutputDto:
    """PDF do currículo revisado e nome de arquivo padronizado."""

    pdf_bytes: bytes
    nome_arquivo: NomeArquivo
