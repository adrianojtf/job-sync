"""Caso de uso: identificar as lacunas da vaga."""

from jobsync.curriculo.service_layer.identificar_lacunas_da_vaga.dtos import IdentificarLacunasDaVagaInputDto
from jobsync.curriculo.service_layer.identificar_lacunas_da_vaga.service import IdentificarLacunasDaVaga

__all__ = ["IdentificarLacunasDaVaga", "IdentificarLacunasDaVagaInputDto"]
