"""Domínio Vaga Externa: busca, extração e descoberta de vagas em fontes externas."""

from jobsync.vaga_externa.domain import (
    BuscadorVagasExternoPort,
    ExtratorTextoPaginaPort,
    FonteVagaExterna,
    VagaComScore,
    VagaExterna,
)

__all__ = [
    "BuscadorVagasExternoPort",
    "ExtratorTextoPaginaPort",
    "FonteVagaExterna",
    "VagaComScore",
    "VagaExterna",
]
