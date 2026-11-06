"""Caso de uso: adaptar um currículo (PDF ou perfil) para uma vaga, em um idioma alvo.

Orquestra as portas de extração e de ajuste de texto por seção sem conhecer os
detalhes de infraestrutura de cada uma (Dependency Inversion). Cada seção do
currículo é ajustada de forma independente: TECHNICAL SKILLS (Tecnologias),
Perfil, Experiências e Formação são lidos e reescritos separadamente.

O resultado é um `RascunhoCurriculoAdaptado`, não um PDF (JOB-0033): o usuário
revisa o rascunho e só então `GerarPdfCurriculoRevisado` gera o arquivo.
"""
from __future__ import annotations

import logging

from jobsync.curriculo import Curriculo, RascunhoCurriculoAdaptado, TipoSecao
from jobsync.curriculo.domain.ajustador_experiencia_port import AjustadorExperienciaPort
from jobsync.curriculo.domain.ajustador_texto_port import AjustadorTextoPort
from jobsync.curriculo.domain.avaliacao_experiencia import ExperienciaParaAvaliacao
from jobsync.curriculo.domain.avaliador_experiencia_port import AvaliadorExperienciaPort
from jobsync.curriculo.domain.extrator_curriculo_port import ExtratorCurriculoPort
from jobsync.curriculo.domain.rascunho_curriculo_adaptado import TITULO_EXPERIENCIAS_PADRAO
from jobsync.curriculo.service_layer.adaptar_curriculo_para_vaga.dtos import (
    AdaptarCurriculoParaVagaInputDto,
    AdaptarCurriculoParaVagaOutputDto,
    AvaliacaoExperienciaAdaptadaDto,
    StatusAvaliacaoAutomatica,
)
from jobsync.curriculo.service_layer.adaptar_curriculo_para_vaga.validator import (
    AdaptarCurriculoParaVagaInputValidator,
)
from jobsync.vaga import AnaliseVaga, AvaliacaoDescricaoVaga
from jobsync.vaga.domain.avaliador_descricao_vaga_port import AvaliadorDescricaoVagaPort
from jobsync.vaga.domain.job_description_analyzer_port import JobDescriptionAnalyzerPort

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)

logger = logging.getLogger(__name__)


class AdaptarCurriculoParaVaga:
    """Caso de uso principal do sistema: lê o currículo, ajusta cada seção via IA e devolve o rascunho."""

    def __init__(
        self,
        extrator: ExtratorCurriculoPort,
        analisador_vaga: JobDescriptionAnalyzerPort,
        ajustador_texto: AjustadorTextoPort,
        avaliador_descricao_vaga: AvaliadorDescricaoVagaPort | None = None,
        ajustador_experiencia: AjustadorExperienciaPort | None = None,
        avaliador_experiencia: AvaliadorExperienciaPort | None = None,
    ) -> None:
        self._extrator = extrator
        self._analisador_vaga = analisador_vaga
        self._ajustador_texto = ajustador_texto
        self._avaliador_descricao_vaga = avaliador_descricao_vaga
        self._ajustador_experiencia = ajustador_experiencia
        self._avaliador_experiencia = avaliador_experiencia

    def executar(self, input_dto: AdaptarCurriculoParaVagaInputDto) -> AdaptarCurriculoParaVagaOutputDto:
        AdaptarCurriculoParaVagaInputValidator.validar(input_dto)
        avaliacao_vaga, status_avaliacao_vaga = self._avaliar_descricao_vaga(input_dto)

        curriculo_original = (
            input_dto.curriculo_pre_montado
            if input_dto.curriculo_pre_montado is not None
            else self._extrator.extrair(input_dto.pdf_curriculo)
        )
        analise_vaga = self._analisador_vaga.analisar(input_dto.descricao_vaga)
        rascunho = self._montar_rascunho(curriculo_original, input_dto, analise_vaga)
        avaliacoes_experiencias = self._avaliar_experiencias(
            rascunho.experiencias or (), input_dto.descricao_vaga
        )
        logger.info(
            "Rascunho adaptado gerado (secoes=%d, experiencias=%d, idioma=%s).",
            len(rascunho.secoes),
            len(rascunho.experiencias or ()),
            input_dto.idioma_alvo,
        )

        return AdaptarCurriculoParaVagaOutputDto(
            rascunho=rascunho,
            curriculo_adaptado=rascunho.para_curriculo(),
            analise_vaga=analise_vaga,
            avaliacao_vaga=avaliacao_vaga,
            status_avaliacao_vaga=status_avaliacao_vaga,
            avaliacoes_experiencias=avaliacoes_experiencias,
        )

    def _avaliar_descricao_vaga(
        self, input_dto: AdaptarCurriculoParaVagaInputDto
    ) -> tuple[AvaliacaoDescricaoVaga | None, StatusAvaliacaoAutomatica | None]:
        if self._avaliador_descricao_vaga is None:
            return None, None
        try:
            return (
                self._avaliador_descricao_vaga.avaliar(input_dto.descricao_vaga),
                StatusAvaliacaoAutomatica.AVALIADA,
            )
        except (RuntimeError, ValueError) as erro:
            logger.warning(
                "A avaliação Jev da descrição ficou indisponível (%s).",
                type(erro).__name__,
            )
            return None, StatusAvaliacaoAutomatica.INDISPONIVEL

    def _montar_rascunho(
        self,
        curriculo: Curriculo,
        input_dto: AdaptarCurriculoParaVagaInputDto,
        analise_vaga: AnaliseVaga,
    ) -> RascunhoCurriculoAdaptado:
        ajustar_experiencias = bool(
            input_dto.experiencias_profissionais and self._ajustador_experiencia
        )
        secao_experiencias = curriculo.obter_secao(TipoSecao.EXPERIENCIAS)
        secoes_de_texto = (
            tuple(secao for secao in curriculo.secoes if secao.tipo != TipoSecao.EXPERIENCIAS)
            if ajustar_experiencias
            else curriculo.secoes
        )
        secoes_ajustadas = tuple(
            self._ajustador_texto.ajustar_secao(
                secao=secao,
                descricao_vaga=input_dto.descricao_vaga,
                idioma_alvo=input_dto.idioma_alvo,
                analise_vaga=analise_vaga,
            )
            for secao in secoes_de_texto
        )
        experiencias = (
            self._ajustar_experiencias(
                input_dto.experiencias_profissionais, input_dto, analise_vaga
            )
            if ajustar_experiencias
            else None
        )

        return RascunhoCurriculoAdaptado(
            nome_completo=curriculo.nome_completo,
            email=curriculo.email,
            linkedin=curriculo.linkedin,
            secoes=secoes_ajustadas,
            experiencias=experiencias,
            titulo_experiencias=(
                secao_experiencias.titulo
                if secao_experiencias is not None
                else TITULO_EXPERIENCIAS_PADRAO
            ),
        )

    def _ajustar_experiencias(
        self,
        experiencias: tuple[ExperienciaParaAvaliacao, ...],
        input_dto: AdaptarCurriculoParaVagaInputDto,
        analise_vaga: AnaliseVaga,
    ) -> tuple[ExperienciaParaAvaliacao, ...]:
        ajustador = self._ajustador_experiencia
        if ajustador is None:
            return ()

        return tuple(
            ExperienciaParaAvaliacao(
                descricao=ajustada.descricao,
                cargo=original.cargo,
                empresa=original.empresa,
                periodo=original.periodo,
            )
            for original in experiencias
            for ajustada in (
                ajustador.ajustar(
                    experiencia=original,
                    descricao_vaga=input_dto.descricao_vaga,
                    idioma_alvo=input_dto.idioma_alvo,
                    analise_vaga=analise_vaga,
                ),
            )
        )

    def _avaliar_experiencias(
        self,
        experiencias: tuple[ExperienciaParaAvaliacao, ...],
        descricao_vaga: str,
    ) -> tuple[AvaliacaoExperienciaAdaptadaDto, ...]:
        if self._avaliador_experiencia is None:
            return ()

        resultados = []
        for experiencia in experiencias:
            try:
                avaliacao = self._avaliador_experiencia.avaliar(
                    experiencia=experiencia,
                    descricao_vaga=descricao_vaga,
                )
                status_avaliacao = StatusAvaliacaoAutomatica.AVALIADA
            except (RuntimeError, ValueError) as erro:
                logger.warning(
                    "A avaliação Jev de uma experiência ficou indisponível (%s).",
                    type(erro).__name__,
                )
                avaliacao = None
                status_avaliacao = StatusAvaliacaoAutomatica.INDISPONIVEL
            resultados.append(
                AvaliacaoExperienciaAdaptadaDto(
                    experiencia=experiencia,
                    status=status_avaliacao,
                    avaliacao=avaliacao,
                )
            )
        return tuple(resultados)
