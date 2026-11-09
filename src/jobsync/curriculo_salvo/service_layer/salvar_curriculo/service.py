"""Caso de uso: salvar um novo currículo na biblioteca de um perfil.

Aplica o limite máximo de currículos salvos por perfil (regra de negócio do
domínio, por isso não fica no validator de input, que cobre apenas
obrigatoriedade/formato).
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from jobsync.curriculo_salvo.domain.curriculo_salvo import CurriculoSalvo
from jobsync.curriculo_salvo.domain.curriculo_salvo_repository import CurriculoSalvoRepository
from jobsync.curriculo_salvo.domain.limite_curriculos_salvos import (
    LIMITE_CURRICULOS_POR_PERFIL,
    LimiteCurriculosSalvosExcedido,
    garantir_espaco,
)
from jobsync.curriculo_salvo.service_layer.salvar_curriculo.dtos import SalvarCurriculoInputDto
from jobsync.curriculo_salvo.service_layer.salvar_curriculo.validator import SalvarCurriculoInputValidator

__all__ = ["LIMITE_CURRICULOS_POR_PERFIL", "LimiteCurriculosSalvosExcedido", "SalvarCurriculo"]


@dataclass
class SalvarCurriculo:
    """Salva um novo currículo na biblioteca do perfil, respeitando o limite máximo."""

    _repositorio_curriculo_salvo: CurriculoSalvoRepository

    def executar(self, input_dto: SalvarCurriculoInputDto) -> CurriculoSalvo:
        SalvarCurriculoInputValidator.validar(input_dto)

        garantir_espaco(
            self._repositorio_curriculo_salvo.contar_por_perfil(input_dto.perfil_identificador)
        )

        curriculo = CurriculoSalvo(
            id=str(uuid.uuid4()),
            perfil_identificador=input_dto.perfil_identificador,
            nome_referencia=input_dto.nome_referencia,
            pdf_bytes=input_dto.pdf_bytes,
            data_upload=datetime.now(),
        )
        return self._repositorio_curriculo_salvo.salvar(curriculo)
