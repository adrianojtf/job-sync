"""Camada de domínio do Currículo Adaptado."""

from jobsync.curriculo_adaptado.domain.curriculo_adaptado import CurriculoAdaptado
from jobsync.curriculo_adaptado.domain.curriculo_adaptado_repository import (
    CurriculoAdaptadoRepository,
)

__all__ = ["CurriculoAdaptado", "CurriculoAdaptadoRepository"]
