"""Adapters concretos do domínio Currículo Adaptado."""

from jobsync.curriculo_adaptado.adapters.curriculo_adaptado_repository_fake import (
    CurriculoAdaptadoRepositoryFake,
)
from jobsync.curriculo_adaptado.adapters.curriculo_adaptado_repository_impl import (
    CurriculoAdaptadoRepositoryImpl,
)

__all__ = ["CurriculoAdaptadoRepositoryFake", "CurriculoAdaptadoRepositoryImpl"]
