"""Caso de uso: candidatura em um clique a uma vaga descoberta."""
from .dtos import CandidatarNaVagaExternaInputDto, CandidatarNaVagaExternaOutputDto
from .use_case import CandidatarNaVagaExterna
from .validator import CandidatarNaVagaExternaInputValidator

__all__ = [
    "CandidatarNaVagaExterna",
    "CandidatarNaVagaExternaInputDto",
    "CandidatarNaVagaExternaOutputDto",
    "CandidatarNaVagaExternaInputValidator",
]
