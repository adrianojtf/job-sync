"""Caso de uso: confirmar a candidatura a partir do currículo ajustado para uma vaga.

Cria, de uma vez, o currículo salvo com o PDF gerado, a vaga (já convertida) e a candidatura
em APLICADO. Usa apenas portas de repositório dos domínios envolvidos, sem chamar outro caso de uso.

Os repositórios gravam de forma independente (não há transação única), então a ordem importa:
a candidatura referencia a vaga e o currículo por chave estrangeira, e a vaga é marcada como
convertida antes da candidatura para que, se a candidatura falhar, nada fique visível em
"Vagas salvas". O currículo salvo é o único registro desfeito (compensação) nas falhas.
"""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from jobsync.shared_kernel.domain.relogio import agora_utc

from jobsync.candidatura.domain.candidatura import Candidatura
from jobsync.candidatura.domain.candidatura_repository import CandidaturaRepository
from jobsync.candidatura.service_layer.confirmar_candidatura_ajustada.dtos import (
    ConfirmarCandidaturaAjustadaInputDto,
)
from jobsync.candidatura.service_layer.confirmar_candidatura_ajustada.validator import (
    ConfirmarCandidaturaAjustadaInputValidator,
)
from jobsync.curriculo_salvo.domain.curriculo_salvo import CurriculoSalvo
from jobsync.curriculo_salvo.domain.curriculo_salvo_repository import CurriculoSalvoRepository
from jobsync.curriculo_salvo.domain.limite_curriculos_salvos import garantir_espaco
from jobsync.vaga.domain.vaga import Vaga
from jobsync.vaga.domain.vaga_repository import VagaRepository

logger = logging.getLogger(__name__)


@dataclass
class ConfirmarCandidaturaAjustada:
    """Registra a candidatura APLICADO com a vaga e o PDF gerado na tela de ajuste."""

    repositorio_candidatura: CandidaturaRepository
    repositorio_vaga: VagaRepository
    repositorio_curriculo_salvo: CurriculoSalvoRepository

    def executar(self, input_dto: ConfirmarCandidaturaAjustadaInputDto) -> Candidatura:
        ConfirmarCandidaturaAjustadaInputValidator.validar(input_dto)
        garantir_espaco(self.repositorio_curriculo_salvo.contar_por_perfil(input_dto.perfil_identificador))

        agora = agora_utc()
        curriculo = self.repositorio_curriculo_salvo.salvar(
            CurriculoSalvo(
                id=str(uuid.uuid4()),
                perfil_identificador=input_dto.perfil_identificador,
                nome_referencia=input_dto.nome_arquivo,
                pdf_bytes=input_dto.pdf_bytes,
                data_upload=agora,
            )
        )
        try:
            vaga = self.repositorio_vaga.salvar(
                Vaga(
                    id=str(uuid.uuid4()),
                    perfil_identificador=input_dto.perfil_identificador,
                    texto_descricao=input_dto.descricao_vaga,
                    data_captura=agora,
                )
            )
            self.repositorio_vaga.marcar_como_convertida(vaga.id)
            candidatura = self.repositorio_candidatura.salvar(
                Candidatura.nova(
                    perfil_identificador=input_dto.perfil_identificador,
                    vaga_id=vaga.id,
                    curriculo_salvo_id=curriculo.id,
                    empresa=input_dto.empresa,
                    cargo=input_dto.cargo,
                    agora=agora,
                )
            )
        except Exception as erro:
            self._desfazer_curriculo_salvo(curriculo, erro)
            raise

        logger.info(
            "Candidatura confirmada: candidatura_id=%s vaga_id=%s curriculo_salvo_id=%s pdf_bytes=%d",
            candidatura.id,
            candidatura.vaga_id,
            curriculo.id,
            len(input_dto.pdf_bytes),
        )
        return candidatura

    def _desfazer_curriculo_salvo(self, curriculo: CurriculoSalvo, erro: Exception) -> None:
        try:
            self.repositorio_curriculo_salvo.remover(curriculo.id, curriculo.perfil_identificador)
        except Exception as erro_da_compensacao:
            logger.warning(
                "Não foi possível remover o currículo salvo %s ao desfazer a confirmação (%s, depois %s)",
                curriculo.id,
                type(erro).__name__,
                type(erro_da_compensacao).__name__,
            )
            return
        logger.warning(
            "Confirmação de candidatura desfeita: currículo salvo %s removido (%s)",
            curriculo.id,
            type(erro).__name__,
        )
