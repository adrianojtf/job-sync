"""Domínio Currículo Adaptado: o currículo adaptado para uma vaga, guardado para edição e reuso."""

from jobsync.curriculo_adaptado.domain.curriculo_adaptado import CurriculoAdaptado
from jobsync.curriculo_adaptado.domain.curriculo_adaptado_repository import (
    CurriculoAdaptadoRepository,
)

__all__ = ["CurriculoAdaptado", "CurriculoAdaptadoRepository"]
