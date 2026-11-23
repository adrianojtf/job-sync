"""Caso de uso: adaptar um currículo (PDF ou perfil) para uma vaga, em um idioma alvo.

Orquestra as portas de extração e de ajuste de texto por seção sem conhecer os
detalhes de infraestrutura de cada uma (Dependency Inversion). Cada seção do
currículo é ajustada de forma independente: SKILLS (Competências),
Perfil, Experiências e Formação são lidos e reescritos separadamente.

O resultado é um `RascunhoCurriculoAdaptado`, não um PDF (JOB-0033): o usuário
revisa o rascunho e só então `GerarPdfCurriculoRevisado` gera o arquivo.
"""
from __future__ import annotations

import logging

from jobsync.curriculo import (
    ContextoVaga,
    Curriculo,
    ExperienciaAdaptada,
    IdentificadorEquivalenciasPort,
    PlanoAdaptacao,
    RascunhoCurriculoAdaptado,
    TipoSecao,
)
from jobsync.curriculo.domain.ajustador_experiencia_port import AjustadorExperienciaPort
from jobsync.curriculo.domain.ajustador_texto_port import AjustadorTextoPort
from jobsync.curriculo.domain.avaliacao_experiencia import ExperienciaParaAvaliacao
from jobsync.curriculo.domain.avaliador_experiencia_port import AvaliadorExperienciaPort
from jobsync.curriculo.domain.extrator_curriculo_port import ExtratorCurriculoPort
from jobsync.curriculo.domain.competencias import (
    CategoriaCompetencia,
    categorias_de_texto,
)
from jobsync.curriculo.domain.selecao_de_competencias import (
    ResultadoDaSelecao,
    SelecaoDeCompetencias,
    limitar_ao_teto,
    restringir_aos_permitidos,
)
from jobsync.curriculo.domain.rascunho_curriculo_adaptado import (
    TITULO_COMPETENCIAS_PADRAO,
    TITULO_EXPERIENCIAS_PADRAO,
)
from jobsync.curriculo.service_layer.adaptar_curriculo_para_vaga.dtos import (
    AdaptarCurriculoParaVagaInputDto,
    AdaptarCurriculoParaVagaOutputDto,
    AvaliacaoExperienciaAdaptadaDto,
    StatusAvaliacaoAutomatica,
)
from jobsync.curriculo.service_layer.adaptar_curriculo_para_vaga.validator import (
    AdaptarCurriculoParaVagaInputValidator,
)
from jobsync.vaga import AvaliacaoDescricaoVaga
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
        identificador_equivalencias: IdentificadorEquivalenciasPort | None = None,
    ) -> None:
        self._extrator = extrator
        self._analisador_vaga = analisador_vaga
        self._ajustador_texto = ajustador_texto
        self._avaliador_descricao_vaga = avaliador_descricao_vaga
        self._ajustador_experiencia = ajustador_experiencia
        self._avaliador_experiencia = avaliador_experiencia
        self._identificador_equivalencias = identificador_equivalencias

    def executar(self, input_dto: AdaptarCurriculoParaVagaInputDto) -> AdaptarCurriculoParaVagaOutputDto:
        AdaptarCurriculoParaVagaInputValidator.validar(input_dto)
        avaliacao_vaga, status_avaliacao_vaga = self._avaliar_descricao_vaga(input_dto)

        curriculo_original = (
            input_dto.curriculo_pre_montado
            if input_dto.curriculo_pre_montado is not None
            else self._extrator.extrair(input_dto.pdf_curriculo)
        )
        contexto = ContextoVaga(
            descricao_vaga=input_dto.descricao_vaga,
            idioma_alvo=input_dto.idioma_alvo,
            analise_vaga=self._analisador_vaga.analisar(input_dto.descricao_vaga),
            cargo_alvo=input_dto.cargo_alvo,
        )
        rascunho = self._montar_rascunho(curriculo_original, input_dto, contexto)
        avaliacoes_experiencias = self._avaliar_experiencias(
            tuple(experiencia.para_avaliacao() for experiencia in rascunho.experiencias or ()),
            input_dto.descricao_vaga,
        )
        logger.info(
            "Rascunho adaptado gerado (secoes=%d, experiencias=%d, idioma=%s).",
            len(rascunho.secoes),
            len(rascunho.experiencias or ()),
            input_dto.idioma_alvo,
        )

        return AdaptarCurriculoParaVagaOutputDto(
            rascunho=rascunho,
            curriculo_adaptado=rascunho.para_curriculo(input_dto.idioma_alvo),
            analise_vaga=contexto.analise_vaga,
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
        contexto: ContextoVaga,
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
        plano = (
            self._planejar(input_dto.experiencias_profissionais, contexto)
            if ajustar_experiencias
            else PlanoAdaptacao.vazio()
        )
        selecao = self._selecionar_competencias(curriculo, input_dto, contexto, plano)
        secoes_ajustadas: list[SecaoCurriculo] = []
        competencias: tuple[CategoriaCompetencia, ...] = ()
        titulo_competencias = TITULO_COMPETENCIAS_PADRAO
        for secao in secoes_de_texto:
            if secao.tipo == TipoSecao.TECNOLOGIAS:
                ajustada = self._ajustador_texto.ajustar_secao(
                    secao=secao,
                    contexto=contexto,
                    ajustes=plano.equivalencias_aplicadas,
                    itens_permitidos=selecao.permitidos,
                )
                competencias = self._filtrar_competencias(ajustada, selecao)
                titulo_competencias = ajustada.titulo
            else:
                secoes_ajustadas.append(
                    self._ajustador_texto.ajustar_secao(
                        secao=secao, contexto=contexto, ajustes=plano.equivalencias_aplicadas
                    )
                )
        experiencias = (
            self._ajustar_experiencias(input_dto.experiencias_profissionais, contexto, plano)
            if ajustar_experiencias
            else None
        )

        return RascunhoCurriculoAdaptado(
            nome_completo=curriculo.nome_completo,
            email=curriculo.email,
            linkedin=curriculo.linkedin,
            secoes=tuple(secoes_ajustadas),
            competencias=competencias or None,
            titulo_competencias=titulo_competencias,
            lacunas_tecnologia=selecao.lacunas,
            experiencias=experiencias,
            titulo_experiencias=(
                secao_experiencias.titulo
                if secao_experiencias is not None
                else TITULO_EXPERIENCIAS_PADRAO
            ),
            ajustes_tecnologia=plano.ajustes,
        )

    def _selecionar_competencias(
        self,
        curriculo: Curriculo,
        input_dto: AdaptarCurriculoParaVagaInputDto,
        contexto: ContextoVaga,
        plano: PlanoAdaptacao,
    ) -> ResultadoDaSelecao:
        """O domínio decide o que pode entrar em Competências; a IA só agrupa e ordena (JOB-0044)."""
        secao_tecnologias = curriculo.obter_secao(TipoSecao.TECNOLOGIAS)
        itens = (
            tuple(tag for categoria in categorias_de_texto(secao_tecnologias.conteudo) for tag in categoria.tags)
            if secao_tecnologias is not None
            else ()
        )
        if input_dto.experiencias_profissionais:
            textos = tuple(
                f"{experiencia.cargo}\n{experiencia.descricao}"
                for experiencia in input_dto.experiencias_profissionais
            )
        else:
            secao_experiencias = curriculo.obter_secao(TipoSecao.EXPERIENCIAS)
            textos = (secao_experiencias.conteudo,) if secao_experiencias is not None else ()
        selecao = SelecaoDeCompetencias().selecionar(
            itens, textos, contexto.analise_vaga.requisitos, plano.equivalencias_aplicadas
        )
        logger.info(
            "Competências selecionadas (itens=%d, permitidos=%d, lacunas=%d).",
            len(itens),
            len(selecao.permitidos),
            len(selecao.lacunas),
        )
        return selecao

    @staticmethod
    def _filtrar_competencias(
        secao: SecaoCurriculo, selecao: ResultadoDaSelecao
    ) -> tuple[CategoriaCompetencia, ...]:
        """Descarta o que a IA acrescentou fora dos permitidos e aplica o teto."""
        da_ia = categorias_de_texto(secao.conteudo)
        permitidas = restringir_aos_permitidos(da_ia, selecao.permitidos)
        limitadas = limitar_ao_teto(permitidas, selecao.relevantes)
        descartados = sum(len(c.tags) for c in da_ia) - sum(len(c.tags) for c in permitidas)
        cortados = sum(len(c.tags) for c in permitidas) - sum(len(c.tags) for c in limitadas)
        logger.info("Competências filtradas (fora dos permitidos=%d, cortados pelo teto=%d).", descartados, cortados)
        return limitadas

    def _planejar(
        self,
        experiencias: tuple[ExperienciaParaAvaliacao, ...],
        contexto: ContextoVaga,
    ) -> PlanoAdaptacao:
        """Aponta equivalências via IA e as distribui no domínio; falha da IA vira plano vazio."""
        if self._identificador_equivalencias is None:
            return PlanoAdaptacao.vazio()
        try:
            equivalencias = self._identificador_equivalencias.identificar(experiencias, contexto)
        except (RuntimeError, ValueError) as erro:
            logger.warning(
                "A identificação de tecnologias equivalentes ficou indisponível (%s).",
                type(erro).__name__,
            )
            return PlanoAdaptacao.vazio()

        plano = PlanoAdaptacao.distribuir(experiencias, equivalencias)
        logger.info(
            "Plano de tecnologias gerado (equivalencias=%d, trocas=%d, manutencoes=%d).",
            len(equivalencias),
            len(plano.ajustes),
            len(plano.manutencoes),
        )
        return plano

    def _ajustar_experiencias(
        self,
        experiencias: tuple[ExperienciaParaAvaliacao, ...],
        contexto: ContextoVaga,
        plano: PlanoAdaptacao,
    ) -> tuple[ExperienciaAdaptada, ...]:
        ajustador = self._ajustador_experiencia
        if ajustador is None:
            return ()

        self._registrar_banco_de_conquistas(experiencias)
        return tuple(
            ajustador.ajustar(
                experiencia=original, contexto=contexto, diretrizes=plano.diretrizes(indice)
            )
            for indice, original in enumerate(experiencias)
        )

    @staticmethod
    def _registrar_banco_de_conquistas(experiencias: tuple[ExperienciaParaAvaliacao, ...]) -> None:
        """Log sem o texto das conquistas (dado pessoal): só quantas experiências têm banco."""
        com_banco = [experiencia for experiencia in experiencias if experiencia.conquistas]
        if com_banco:
            logger.info(
                "Banco de conquistas enviado à adaptação (experiencias_com_banco=%d, conquistas=%d).",
                len(com_banco),
                sum(len(experiencia.conquistas) for experiencia in com_banco),
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
