"""Caso de uso: gerar o PDF do currículo a partir do rascunho revisado e confirmado.

É a etapa de confirmação da revisão (JOB-0033): não chama a IA, apenas
converte o rascunho no Curriculo e aciona a porta de geração de PDF.
"""
from __future__ import annotations

import logging

from jobsync.curriculo.domain.gerador_pdf_port import GeradorPdfPort
from jobsync.curriculo.service_layer.gerar_pdf_curriculo_revisado.dtos import (
    GerarPdfCurriculoRevisadoInputDto,
    GerarPdfCurriculoRevisadoOutputDto,
)
from jobsync.curriculo.service_layer.gerar_pdf_curriculo_revisado.validator import (
    GerarPdfCurriculoRevisadoInputValidator,
)
from jobsync.shared_kernel.domain import NomeArquivo

logger = logging.getLogger(__name__)


class GerarPdfCurriculoRevisado:
    """Gera o PDF final a partir do conteúdo revisado pelo usuário."""

    def __init__(self, gerador_pdf: GeradorPdfPort) -> None:
        self._gerador_pdf = gerador_pdf

    def executar(
        self, input_dto: GerarPdfCurriculoRevisadoInputDto
    ) -> GerarPdfCurriculoRevisadoOutputDto:
        GerarPdfCurriculoRevisadoInputValidator.validar(input_dto)
        rascunho = input_dto.rascunho
        curriculo = rascunho.para_curriculo()

        pdf_bytes = self._gerador_pdf.gerar(curriculo, input_dto.idioma_alvo)
        logger.info(
            "PDF gerado a partir de rascunho revisado (secoes=%d, experiencias=%d, idioma=%s).",
            len(curriculo.secoes),
            len(rascunho.experiencias or ()),
            input_dto.idioma_alvo,
        )

        return GerarPdfCurriculoRevisadoOutputDto(
            pdf_bytes=pdf_bytes,
            nome_arquivo=NomeArquivo.criar(
                nome_completo=rascunho.nome_completo,
                cargo=input_dto.cargo_alvo,
                empresa=input_dto.empresa_alvo,
                data=input_dto.data_referencia,
            ),
        )
