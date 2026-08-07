"""Caso de uso: salvar (criar ou atualizar) o perfil estruturado de um login."""
from __future__ import annotations

from dataclasses import dataclass

from jobsync.perfil_estruturado.domain.perfil_estruturado import PerfilEstruturado
from jobsync.perfil_estruturado.domain.perfil_estruturado_repository import PerfilEstruturadoRepository
from jobsync.perfil_estruturado.service_layer.salvar_perfil_estruturado.dtos import SalvarPerfilEstruturadoInputDto
from jobsync.perfil_estruturado.service_layer.salvar_perfil_estruturado.validator import SalvarPerfilEstruturadoInputValidator


@dataclass
class SalvarPerfilEstruturado:
    """Persiste o perfil estruturado (upsert — uma versão por perfil, sem histórico)."""

    repositorio: PerfilEstruturadoRepository

    def executar(self, input_dto: SalvarPerfilEstruturadoInputDto) -> PerfilEstruturado:
        SalvarPerfilEstruturadoInputValidator.validar(input_dto)

        perfil = PerfilEstruturado(
            perfil_identificador=input_dto.perfil_identificador,
            nome_completo=input_dto.nome_completo,
            email=input_dto.email,
            linkedin=input_dto.linkedin,
            resumo_profissional=input_dto.resumo_profissional,
            experiencias=input_dto.experiencias,
            formacoes=input_dto.formacoes,
            certificacoes=input_dto.certificacoes,
            idiomas=input_dto.idiomas,
            tecnologias=input_dto.tecnologias,
        )
        return self.repositorio.salvar(perfil)
