"""Caso de uso: salvar (criar ou atualizar) o perfil estruturado de um login."""
from __future__ import annotations

from application.use_cases.salvar_perfil_estruturado.dtos import SalvarPerfilEstruturadoInputDto
from application.use_cases.salvar_perfil_estruturado.validator import (
    SalvarPerfilEstruturadoInputValidator,
)
from domain.perfil_estruturado import PerfilEstruturado
from domain.perfil_estruturado.perfil_estruturado_repository import PerfilEstruturadoRepository


class SalvarPerfilEstruturado:
    """Persiste o perfil estruturado (upsert — uma versão por perfil, sem histórico)."""

    def __init__(self, repositorio: PerfilEstruturadoRepository) -> None:
        self._repositorio = repositorio

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
        return self._repositorio.salvar(perfil)
