"""Caso de uso: salvar (criar ou atualizar) o perfil estruturado de um login."""
from __future__ import annotations

import logging
from dataclasses import dataclass

from jobsync.perfil_estruturado.domain.perfil_estruturado import PerfilEstruturado
from jobsync.perfil_estruturado.domain.perfil_estruturado_repository import PerfilEstruturadoRepository
from jobsync.perfil_estruturado.service_layer.salvar_perfil_estruturado.dtos import (
    SalvarPerfilEstruturadoInputDto,
    SalvarPerfilEstruturadoOutputDto,
)
from jobsync.perfil_estruturado.service_layer.salvar_perfil_estruturado.validator import SalvarPerfilEstruturadoInputValidator

logger = logging.getLogger(__name__)


@dataclass
class SalvarPerfilEstruturado:
    """Persiste o perfil estruturado (upsert — uma versão por perfil, sem histórico)."""

    repositorio: PerfilEstruturadoRepository

    def executar(self, input_dto: SalvarPerfilEstruturadoInputDto) -> SalvarPerfilEstruturadoOutputDto:
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
        tecnologias_incluidas = perfil.tecnologias_ausentes()
        salvo = self.repositorio.salvar(perfil.com_tecnologias_das_experiencias())
        logger.info("Tecnologias incluidas pelas skills (quantidade=%d).", len(tecnologias_incluidas))
        return SalvarPerfilEstruturadoOutputDto(perfil=salvo, tecnologias_incluidas=tecnologias_incluidas)
