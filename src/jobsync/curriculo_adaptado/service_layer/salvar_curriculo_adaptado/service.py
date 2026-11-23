"""Caso de uso: salvar o currículo adaptado confirmado na revisão e gerar o PDF dele (JOB-0041).

O PDF é gerado antes de gravar: se a geração falhar, nada fica salvo.
"""
from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import datetime

from jobsync.curriculo import GeradorPdfPort
from jobsync.curriculo_adaptado.domain.curriculo_adaptado import CurriculoAdaptado
from jobsync.curriculo_adaptado.domain.curriculo_adaptado_repository import (
    CurriculoAdaptadoRepository,
)
from jobsync.curriculo_adaptado.service_layer.resultado_com_pdf import CurriculoAdaptadoComPdf
from jobsync.curriculo_adaptado.service_layer.salvar_curriculo_adaptado.dtos import (
    SalvarCurriculoAdaptadoInputDto,
)
from jobsync.curriculo_adaptado.service_layer.salvar_curriculo_adaptado.validator import (
    SalvarCurriculoAdaptadoInputValidator,
)
from jobsync.shared_kernel.domain import NomeArquivo
from jobsync.shared_kernel.domain.relogio import agora_utc

logger = logging.getLogger(__name__)


class SalvarCurriculoAdaptado:
    def __init__(
        self,
        repositorio: CurriculoAdaptadoRepository,
        gerador_pdf: GeradorPdfPort,
        relogio: Callable[[], datetime] = agora_utc,
    ) -> None:
        self._repositorio = repositorio
        self._gerador_pdf = gerador_pdf
        self._relogio = relogio

    def executar(self, input_dto: SalvarCurriculoAdaptadoInputDto) -> CurriculoAdaptadoComPdf:
        SalvarCurriculoAdaptadoInputValidator.validar(input_dto)
        rascunho = input_dto.rascunho
        nome_arquivo = NomeArquivo.criar(
            nome_completo=rascunho.nome_completo,
            cargo=input_dto.cargo_alvo,
            empresa=input_dto.empresa_alvo,
            data=input_dto.data_referencia,
        )
        pdf_bytes = self._gerador_pdf.gerar(
            rascunho.para_curriculo(input_dto.idioma_alvo), input_dto.idioma_alvo
        )

        curriculo = self._repositorio.salvar(
            CurriculoAdaptado.novo(
                perfil_identificador=input_dto.perfil_identificador,
                nome_referencia=nome_arquivo.valor,
                cargo_alvo=input_dto.cargo_alvo,
                empresa_alvo=input_dto.empresa_alvo,
                idioma_alvo=input_dto.idioma_alvo,
                descricao_vaga=input_dto.descricao_vaga,
                analise_vaga=input_dto.analise_vaga,
                rascunho=rascunho,
                agora=self._relogio(),
            )
        )
        logger.info(
            "Currículo adaptado salvo (id=%s, categorias=%d, experiencias=%d, pdf_bytes=%d).",
            curriculo.id,
            len(rascunho.competencias or ()),
            len(rascunho.experiencias or ()),
            len(pdf_bytes),
        )
        return CurriculoAdaptadoComPdf(curriculo, pdf_bytes, nome_arquivo)
