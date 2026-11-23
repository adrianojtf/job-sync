"""Resultado dos casos de uso que salvam o currículo adaptado e geram o PDF dele."""
from __future__ import annotations

from dataclasses import dataclass

from jobsync.curriculo_adaptado.domain.curriculo_adaptado import CurriculoAdaptado
from jobsync.shared_kernel.domain import NomeArquivo


@dataclass(frozen=True)
class CurriculoAdaptadoComPdf:
    curriculo: CurriculoAdaptado
    pdf_bytes: bytes
    nome_arquivo: NomeArquivo
