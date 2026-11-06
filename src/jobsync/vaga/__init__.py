"""Domínio Vaga: captura e análise de descrições de vaga."""

from jobsync.vaga.domain.analise_vaga import (
    AnaliseVaga,
    CategoriaRequisitoTecnico,
    OrigemRequisitoTecnico,
    RequisitoTecnico,
    TipoRequisitoTecnico,
)
from jobsync.vaga.domain.avaliacao_descricao_vaga import AvaliacaoDescricaoVaga
from jobsync.vaga.domain.avaliador_descricao_vaga_port import (
    AvaliadorDescricaoVagaPort,
)
from jobsync.vaga.domain.vaga import Vaga
from jobsync.vaga.domain.vaga_repository import VagaRepository

__all__ = [
    "AnaliseVaga",
    "AvaliacaoDescricaoVaga",
    "AvaliadorDescricaoVagaPort",
    "CategoriaRequisitoTecnico",
    "OrigemRequisitoTecnico",
    "RequisitoTecnico",
    "TipoRequisitoTecnico",
    "Vaga",
    "VagaRepository",
]
