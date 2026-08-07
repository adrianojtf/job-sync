"""Caso de uso: criar uma candidatura a partir de uma vaga capturada e um currículo salvo.

Ao criar a candidatura, a vaga de origem é marcada como convertida, saindo
da lista de "vagas capturadas pendentes" (VagaRepository).
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from jobsync.candidatura.domain.candidatura import Candidatura, MudancaStatus, StatusCandidatura
from jobsync.candidatura.domain.candidatura_repository import CandidaturaRepository
from jobsync.candidatura.service_layer.criar_candidatura.dtos import CriarCandidaturaInputDto
from jobsync.candidatura.service_layer.criar_candidatura.validator import CriarCandidaturaInputValidator
from jobsync.vaga.domain.vaga_repository import VagaRepository


@dataclass
class CriarCandidatura:
    """Cria uma candidatura com status inicial APLICADO e marca a vaga como convertida."""

    repositorio_candidatura: CandidaturaRepository
    repositorio_vaga: VagaRepository

    def executar(self, input_dto: CriarCandidaturaInputDto) -> Candidatura:
        CriarCandidaturaInputValidator.validar(input_dto)

        agora = datetime.now()
        candidatura = Candidatura(
            id=str(uuid.uuid4()),
            perfil_identificador=input_dto.perfil_identificador,
            vaga_id=input_dto.vaga_id,
            curriculo_salvo_id=input_dto.curriculo_salvo_id,
            empresa=input_dto.empresa,
            cargo=input_dto.cargo,
            status=StatusCandidatura.APLICADO,
            data_aplicacao=agora,
            historico_status=(MudancaStatus(status=StatusCandidatura.APLICADO, data=agora),),
        )
        candidatura_salva = self.repositorio_candidatura.salvar(candidatura)
        self.repositorio_vaga.marcar_como_convertida(input_dto.vaga_id)
        return candidatura_salva
