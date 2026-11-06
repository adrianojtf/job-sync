"""Caso de uso: adaptar um currículo (PDF) para uma vaga específica, em um idioma alvo.

Orquestra as três portas (extração, ajuste de texto por seção, geração de PDF)
sem conhecer os detalhes de infraestrutura de cada uma (Dependency Inversion).
Cada seção do currículo é ajustada de forma independente, conforme solicitado:
TECHNICAL SKILLS (Tecnologias), Perfil, Experiências e Formação são lidos e
reescritos separadamente antes de serem remontados no currículo final.
"""
from __future__ import annotations

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)

logger = logging.getLogger(__name__)

from jobsync.curriculo.service_layer.adaptar_curriculo_para_vaga.dtos import (
    AdaptarCurriculoParaVagaInputDto,
    AdaptarCurriculoParaVagaOutputDto,
)
from jobsync.curriculo.service_layer.adaptar_curriculo_para_vaga.validator import (
    AdaptarCurriculoParaVagaInputValidator,
)
from jobsync.curriculo import Curriculo, SecaoCurriculo, TipoSecao
from jobsync.curriculo.domain.ajustador_experiencia_port import AjustadorExperienciaPort
from jobsync.curriculo.domain.ajustador_texto_port import AjustadorTextoPort
from jobsync.curriculo.domain.avaliacao_experiencia import ExperienciaParaAvaliacao
from jobsync.curriculo.domain.avaliador_experiencia_port import AvaliadorExperienciaPort
from jobsync.curriculo.domain.extrator_curriculo_port import ExtratorCurriculoPort
from jobsync.curriculo.domain.gerador_pdf_port import GeradorPdfPort
from jobsync.curriculo.service_layer.adaptar_curriculo_para_vaga.dtos import (
    AvaliacaoExperienciaAdaptadaDto,
    StatusAvaliacaoAutomatica,
)
from jobsync.shared_kernel.domain import NomeArquivo
from jobsync.vaga import AnaliseVaga, AvaliacaoDescricaoVaga
from jobsync.vaga.domain.avaliador_descricao_vaga_port import AvaliadorDescricaoVagaPort
from jobsync.vaga.domain.job_description_analyzer_port import JobDescriptionAnalyzerPort


class AdaptarCurriculoParaVaga:
    """Caso de uso principal do sistema: lê o PDF, ajusta cada seção via IA e gera o PDF final."""

    def __init__(
        self,
        extrator: ExtratorCurriculoPort,
        analisador_vaga: JobDescriptionAnalyzerPort,
        ajustador_texto: AjustadorTextoPort,
        gerador_pdf: GeradorPdfPort,
        avaliador_descricao_vaga: AvaliadorDescricaoVagaPort | None = None,
        ajustador_experiencia: AjustadorExperienciaPort | None = None,
        avaliador_experiencia: AvaliadorExperienciaPort | None = None,
    ) -> None:
        self._extrator = extrator
        self._analisador_vaga = analisador_vaga
        self._ajustador_texto = ajustador_texto
        self._gerador_pdf = gerador_pdf
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
        curriculo_adaptado, experiencias_adaptadas = self._ajustar_todas_as_secoes(
            curriculo_original, input_dto, analise_vaga
        )
        pdf_bytes = self._gerador_pdf.gerar(curriculo_adaptado, input_dto.idioma_alvo)
        avaliacoes_experiencias = self._avaliar_experiencias(
            experiencias_adaptadas, input_dto.descricao_vaga
        )

        nome_arquivo = NomeArquivo.criar(
            nome_completo=curriculo_original.nome_completo,
            cargo=input_dto.cargo_alvo,
            empresa=input_dto.empresa_alvo,
            data=input_dto.data_referencia,
        )

        return AdaptarCurriculoParaVagaOutputDto(
            pdf_bytes=pdf_bytes,
            nome_arquivo=nome_arquivo,
            curriculo_adaptado=curriculo_adaptado,
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

    def _ajustar_todas_as_secoes(
        self,
        curriculo: Curriculo,
        input_dto: AdaptarCurriculoParaVagaInputDto,
        analise_vaga: AnaliseVaga,
    ) -> tuple[Curriculo, tuple[ExperienciaParaAvaliacao, ...]]:
        curriculo_atualizado = curriculo
        experiencias_adaptadas: tuple[ExperienciaParaAvaliacao, ...] = ()
        ajustar_experiencias = bool(
            input_dto.experiencias_profissionais and self._ajustador_experiencia
        )
        encontrou_secao_experiencias = False

        for secao_original in curriculo.secoes:
            if ajustar_experiencias and secao_original.tipo == TipoSecao.EXPERIENCIAS:
                experiencias_adaptadas = self._ajustar_experiencias(
                    input_dto.experiencias_profissionais,
                    input_dto,
                    analise_vaga,
                )
                secao_ajustada = self._montar_secao_experiencias(
                    experiencias_adaptadas, titulo=secao_original.titulo
                )
                curriculo_atualizado = curriculo_atualizado.substituir_secao(
                    secao_ajustada
                )
                encontrou_secao_experiencias = True
                continue

            secao_ajustada = self._ajustador_texto.ajustar_secao(                
                secao=secao_original,
                descricao_vaga=input_dto.descricao_vaga,
                idioma_alvo=input_dto.idioma_alvo,
                analise_vaga=analise_vaga,
            )

            curriculo_atualizado = curriculo_atualizado.substituir_secao(secao_ajustada)

        if ajustar_experiencias and not encontrou_secao_experiencias:
            experiencias_adaptadas = self._ajustar_experiencias(
                input_dto.experiencias_profissionais,
                input_dto,
                analise_vaga,
            )
            curriculo_atualizado = curriculo_atualizado.substituir_secao(
                self._montar_secao_experiencias(experiencias_adaptadas)
            )

        return curriculo_atualizado, experiencias_adaptadas

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

    @staticmethod
    def _montar_secao_experiencias(
        experiencias: tuple[ExperienciaParaAvaliacao, ...],
        titulo: str = "Experiências",
    ) -> SecaoCurriculo:
        blocos = []
        for experiencia in experiencias:
            identificacao = " — ".join(
                valor.strip()
                for valor in (experiencia.cargo, experiencia.empresa)
                if valor and valor.strip()
            )
            if experiencia.periodo and experiencia.periodo.strip():
                identificacao = (
                    f"{identificacao} ({experiencia.periodo.strip()})"
                    if identificacao
                    else experiencia.periodo.strip()
                )
            conteudo = "\n".join(
                parte for parte in (identificacao, experiencia.descricao.strip()) if parte
            )
            if conteudo:
                blocos.append(conteudo)
        return SecaoCurriculo(
            tipo=TipoSecao.EXPERIENCIAS,
            titulo=titulo,
            conteudo="\n\n".join(blocos),
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
