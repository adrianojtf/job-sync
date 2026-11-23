"""Caso de uso: salvar a edição de um currículo adaptado e regenerar o PDF dele (JOB-0041).

A vaga, o idioma e o vínculo com o currículo salvo não mudam; só o conteúdo. O PDF é gerado
antes de gravar: se a geração falhar, o currículo continua como estava.
"""
from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import datetime

from jobsync.curriculo import GeradorPdfPort
from jobsync.curriculo_adaptado.domain.curriculo_adaptado_repository import (
    CurriculoAdaptadoRepository,
)
from jobsync.curriculo_adaptado.domain.exceptions import CurriculoAdaptadoNaoEncontrado
from jobsync.curriculo_adaptado.service_layer.atualizar_curriculo_adaptado.dtos import (
    AtualizarCurriculoAdaptadoInputDto,
)
from jobsync.curriculo_adaptado.service_layer.resultado_com_pdf import CurriculoAdaptadoComPdf
from jobsync.curriculo_salvo.domain.curriculo_salvo_repository import CurriculoSalvoRepository
from jobsync.shared_kernel.domain import NomeArquivo
from jobsync.shared_kernel.domain.relogio import agora_utc

logger = logging.getLogger(__name__)


class AtualizarCurriculoAdaptado:
    def __init__(
        self,
        repositorio: CurriculoAdaptadoRepository,
        gerador_pdf: GeradorPdfPort,
        repositorio_curriculo_salvo: CurriculoSalvoRepository | None = None,
        relogio: Callable[[], datetime] = agora_utc,
    ) -> None:
        self._repositorio = repositorio
        self._gerador_pdf = gerador_pdf
        self._repositorio_curriculo_salvo = repositorio_curriculo_salvo
        self._relogio = relogio

    def executar(self, input_dto: AtualizarCurriculoAdaptadoInputDto) -> CurriculoAdaptadoComPdf:
        atual = self._repositorio.buscar(input_dto.curriculo_id, input_dto.perfil_identificador)
        if atual is None:
            raise CurriculoAdaptadoNaoEncontrado()

        rascunho = input_dto.rascunho
        nome_arquivo = NomeArquivo.criar(
            nome_completo=rascunho.nome_completo,
            cargo=atual.cargo_alvo,
            empresa=atual.empresa_alvo,
            data=input_dto.data_referencia,
        )
        pdf_bytes = self._gerador_pdf.gerar(
            rascunho.para_curriculo(atual.idioma_alvo), atual.idioma_alvo
        )

        curriculo = self._repositorio.salvar(atual.com_rascunho_revisado(rascunho, self._relogio()))
        self._atualizar_pdf_salvo(curriculo.curriculo_salvo_id, curriculo.perfil_identificador, pdf_bytes)
        logger.info(
            "Currículo adaptado atualizado (id=%s, categorias=%d, pdf_bytes=%d).",
            curriculo.id,
            len(rascunho.competencias or ()),
            len(pdf_bytes),
        )
        return CurriculoAdaptadoComPdf(curriculo, pdf_bytes, nome_arquivo)

    def _atualizar_pdf_salvo(
        self, curriculo_salvo_id: str | None, perfil_identificador: str, pdf_bytes: bytes
    ) -> None:
        """Leva a edição ao PDF da candidatura. É o último passo: falha vira log, o PDF novo segue."""
        if curriculo_salvo_id is None or self._repositorio_curriculo_salvo is None:
            return
        try:
            self._repositorio_curriculo_salvo.atualizar_pdf(
                curriculo_salvo_id, perfil_identificador, pdf_bytes
            )
        except Exception as erro:
            logger.warning(
                "Não foi possível atualizar o PDF do currículo salvo %s (%s)",
                curriculo_salvo_id,
                type(erro).__name__,
            )
