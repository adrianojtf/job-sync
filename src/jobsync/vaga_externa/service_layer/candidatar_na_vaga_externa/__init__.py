"""Caso de uso: candidatura em um clique a uma vaga descoberta."""

from jobsync.vaga_externa.service_layer.candidatar_na_vaga_externa.dtos import (
    CandidatarNaVagaExternaInputDto,
    CandidatarNaVagaExternaOutputDto,
)
from jobsync.vaga_externa.service_layer.candidatar_na_vaga_externa.service import (
    CandidatarNaVagaExterna,
)
from jobsync.vaga_externa.service_layer.candidatar_na_vaga_externa.validator import (
    CandidatarNaVagaExternaInputValidator,
)

__all__ = [
    "CandidatarNaVagaExterna",
    "CandidatarNaVagaExternaInputDto",
    "CandidatarNaVagaExternaOutputDto",
    "CandidatarNaVagaExternaInputValidator",
]
