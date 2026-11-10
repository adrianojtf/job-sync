"""Caso de uso: registrar uma vaga capturada (via extensão de navegador ou colada manualmente)."""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from jobsync.shared_kernel.domain.relogio import agora_utc

from jobsync.vaga.domain.vaga import Vaga
from jobsync.vaga.domain.vaga_repository import VagaRepository
from jobsync.vaga.service_layer.capturar_vaga.dtos import CapturarVagaInputDto
from jobsync.vaga.service_layer.capturar_vaga.validator import CapturarVagaInputValidator


@dataclass
class CapturarVaga:
    """Persiste uma nova vaga capturada, associada ao perfil informado."""

    _repositorio_vaga: VagaRepository

    def executar(self, input_dto: CapturarVagaInputDto) -> Vaga:
        CapturarVagaInputValidator.validar(input_dto)

        vaga = Vaga(
            id=str(uuid.uuid4()),
            perfil_identificador=input_dto.perfil_identificador,
            texto_descricao=input_dto.texto_descricao,
            url_origem=input_dto.url_origem,
            data_captura=agora_utc(),
        )
        return self._repositorio_vaga.salvar(vaga)
