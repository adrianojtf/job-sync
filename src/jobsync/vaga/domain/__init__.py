"""Camada de domínio da Vaga."""

from jobsync.vaga.domain.analise_vaga import (
    AnaliseVaga,
    CategoriaRequisitoTecnico,
    OrigemRequisitoTecnico,
    RequisitoTecnico,
    TipoRequisitoTecnico,
)
from jobsync.vaga.domain.vaga import Vaga
from jobsync.vaga.domain.vaga_repository import VagaRepository

__all__ = [
    "AnaliseVaga",
    "CategoriaRequisitoTecnico",
    "OrigemRequisitoTecnico",
    "RequisitoTecnico",
    "TipoRequisitoTecnico",
    "Vaga",
    "VagaRepository",
]
