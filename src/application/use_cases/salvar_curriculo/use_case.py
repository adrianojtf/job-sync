"""Caso de uso: salvar um novo currículo na biblioteca de um perfil.

Aplica o limite máximo de currículos salvos por perfil (regra de negócio,
por isso verificada aqui e não no validator de input, que cobre apenas
obrigatoriedade/formato).
"""
from __future__ import annotations

import uuid
from datetime import datetime

from application.use_cases.salvar_curriculo.dtos import SalvarCurriculoInputDto
from application.use_cases.salvar_curriculo.validator import SalvarCurriculoInputValidator
from domain.curriculo_salvo import CurriculoSalvo
from domain.curriculo_salvo.curriculo_salvo_repository import CurriculoSalvoRepository

LIMITE_CURRICULOS_POR_PERFIL = 10


class LimiteCurriculosSalvosExcedido(ValueError):
    """Levantado quando o perfil já atingiu o limite de currículos salvos."""


class SalvarCurriculo:
    """Salva um novo currículo na biblioteca do perfil, respeitando o limite máximo."""

    def __init__(self, repositorio_curriculo_salvo: CurriculoSalvoRepository) -> None:
        self._repositorio_curriculo_salvo = repositorio_curriculo_salvo

    def executar(self, input_dto: SalvarCurriculoInputDto) -> CurriculoSalvo:
        SalvarCurriculoInputValidator.validar(input_dto)

        quantidade_atual = self._repositorio_curriculo_salvo.contar_por_perfil(
            input_dto.perfil_identificador
        )
        if quantidade_atual >= LIMITE_CURRICULOS_POR_PERFIL:
            raise LimiteCurriculosSalvosExcedido(
                f"Limite de {LIMITE_CURRICULOS_POR_PERFIL} currículos salvos atingido. "
                "Remova um currículo existente antes de salvar um novo."
            )

        curriculo = CurriculoSalvo(
            id=str(uuid.uuid4()),
            perfil_identificador=input_dto.perfil_identificador,
            nome_referencia=input_dto.nome_referencia,
            pdf_bytes=input_dto.pdf_bytes,
            data_upload=datetime.now(),
        )
        return self._repositorio_curriculo_salvo.salvar(curriculo)
