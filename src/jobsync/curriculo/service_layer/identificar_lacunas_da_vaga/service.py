"""Caso de uso: identificar as lacunas entre a vaga e o histórico do candidato (JOB-0043).

A etapa de perguntas nunca bloqueia a geração do currículo: falha da IA vira "sem lacunas", como
a identificação de tecnologias equivalentes (`AdaptarCurriculoParaVaga._planejar`).
"""
from __future__ import annotations

import logging

from jobsync.curriculo.domain.identificador_lacunas_port import IdentificadorLacunasPort
from jobsync.curriculo.domain.lacuna_da_vaga import LacunaDaVaga, principais
from jobsync.curriculo.service_layer.identificar_lacunas_da_vaga.dtos import IdentificarLacunasDaVagaInputDto

logger = logging.getLogger(__name__)


class IdentificarLacunasDaVaga:
    """Pede as lacunas à porta de IA e entrega no máximo as 5 principais, sem tema repetido."""

    def __init__(self, identificador: IdentificadorLacunasPort) -> None:
        self._identificador = identificador

    def executar(self, input_dto: IdentificarLacunasDaVagaInputDto) -> tuple[LacunaDaVaga, ...]:
        if input_dto.historico.sem_experiencias():
            return ()
        try:
            lacunas = self._identificador.identificar(input_dto.historico, input_dto.contexto)
        except (RuntimeError, ValueError) as erro:
            logger.warning(
                "A identificação de lacunas da vaga ficou indisponível (%s).", type(erro).__name__
            )
            return ()
        resultado = principais(lacunas)
        logger.info("Lacunas da vaga identificadas (lacunas=%d).", len(resultado))
        return resultado
