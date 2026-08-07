"""Camada de domínio da Vaga Externa."""

from jobsync.vaga_externa.domain.buscador_vagas_externo_port import BuscadorVagasExternoPort
from jobsync.vaga_externa.domain.extrator_texto_pagina_port import ExtratorTextoPaginaPort
from jobsync.vaga_externa.domain.vaga_externa import (
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
