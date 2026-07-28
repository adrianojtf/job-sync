"""Caso de uso: registrar uma vaga capturada (via extensão de navegador ou colada manualmente)."""
from __future__ import annotations

import uuid
from datetime import datetime

from application.use_cases.capturar_vaga.dtos import CapturarVagaInputDto
from application.use_cases.capturar_vaga.validator import CapturarVagaInputValidator
from domain.vaga import Vaga
from domain.vaga.vaga_repository import VagaRepository


class CapturarVaga:
    """Persiste uma nova vaga capturada, associada ao perfil informado."""

    def __init__(self, repositorio_vaga: VagaRepository) -> None:
        self._repositorio_vaga = repositorio_vaga

    def executar(self, input_dto: CapturarVagaInputDto) -> Vaga:
        CapturarVagaInputValidator.validar(input_dto)

        vaga = Vaga(
            id=str(uuid.uuid4()),
            perfil_identificador=input_dto.perfil_identificador,
            texto_descricao=input_dto.texto_descricao,
            url_origem=input_dto.url_origem,
            data_captura=datetime.now(),
        )
        return self._repositorio_vaga.salvar(vaga)
