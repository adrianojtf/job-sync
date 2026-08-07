"""Caso de uso adaptar curriculo para vaga."""

from jobsync.curriculo.service_layer.adaptar_curriculo_para_vaga.dtos import (
    AdaptarCurriculoParaVagaInputDto,
    AdaptarCurriculoParaVagaOutputDto,
)
from jobsync.curriculo.service_layer.adaptar_curriculo_para_vaga.service import AdaptarCurriculoParaVaga

__all__ = [
    "AdaptarCurriculoParaVaga",
    "AdaptarCurriculoParaVagaInputDto",
    "AdaptarCurriculoParaVagaOutputDto",
]
