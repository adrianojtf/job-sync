"""Caso de uso salvar currículo adaptado."""

from jobsync.curriculo_adaptado.service_layer.salvar_curriculo_adaptado.dtos import (
    SalvarCurriculoAdaptadoInputDto,
)
from jobsync.curriculo_adaptado.service_layer.salvar_curriculo_adaptado.service import (
    SalvarCurriculoAdaptado,
)

__all__ = ["SalvarCurriculoAdaptado", "SalvarCurriculoAdaptadoInputDto"]
