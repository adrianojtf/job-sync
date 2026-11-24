"""Validator de input para o caso de uso MigrarExperienciasDoPerfil."""
from __future__ import annotations

from jobsync.perfil_estruturado.service_layer.migrar_experiencias_do_perfil.dtos import (
    MigrarExperienciasDoPerfilInputDto,
)


class MigrarExperienciasDoPerfilInputValidator:
    @staticmethod
    def validar(input_dto: MigrarExperienciasDoPerfilInputDto) -> None:
        if not input_dto.perfil_identificador or not input_dto.perfil_identificador.strip():
            raise ValueError("O identificador do perfil é obrigatório.")
