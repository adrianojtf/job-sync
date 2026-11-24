"""DTO de input para o caso de uso MigrarExperienciasDoPerfil."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MigrarExperienciasDoPerfilInputDto:
    perfil_identificador: str
