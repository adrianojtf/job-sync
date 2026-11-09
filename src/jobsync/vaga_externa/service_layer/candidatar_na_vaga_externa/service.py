"""Caso de uso: candidatura em um clique a uma vaga descoberta.

Implementa o botão "Candidatar": extrai o currículo, analisa a vaga, ajusta
todas as seções (mesma lógica de `AdaptarCurriculoParaVaga`), calcula o ATS
Score e gera a carta de apresentação — sem chamar nenhum outro use case
diretamente, reaproveitando apenas portas e o Domain Service `CalcularAtsScore`.
"""
from __future__ import annotations

from jobsync.ats_score import CalcularAtsScore
from jobsync.curriculo import (
    AjustadorTextoPort,
    ContextoVaga,
    Curriculo,
    ExtratorCurriculoPort,
    GeradorPdfPort,
    GerarCartaApresentacaoPort,
)
from jobsync.shared_kernel.domain import NomeArquivo
from jobsync.vaga import AnaliseVaga
from jobsync.vaga.domain.job_description_analyzer_port import JobDescriptionAnalyzerPort
from jobsync.vaga_externa.service_layer.candidatar_na_vaga_externa.dtos import (
    CandidatarNaVagaExternaInputDto,
    CandidatarNaVagaExternaOutputDto,
)
from jobsync.vaga_externa.service_layer.candidatar_na_vaga_externa.validator import (
    CandidatarNaVagaExternaInputValidator,
)


class CandidatarNaVagaExterna:
    """Prepara os artefatos de candidatura (PDF adaptado + carta) para uma vaga externa."""

    def __init__(
        self,
        extrator: ExtratorCurriculoPort,
        analisador_vaga: JobDescriptionAnalyzerPort,
        ajustador_texto: AjustadorTextoPort,
        gerador_pdf: GeradorPdfPort,
        calcular_ats_score: CalcularAtsScore,
        gerador_carta: GerarCartaApresentacaoPort,
    ) -> None:
        self._extrator = extrator
        self._analisador_vaga = analisador_vaga
        self._ajustador_texto = ajustador_texto
        self._gerador_pdf = gerador_pdf
        self._calcular_ats_score = calcular_ats_score
        self._gerador_carta = gerador_carta

    def executar(self, input_dto: CandidatarNaVagaExternaInputDto) -> CandidatarNaVagaExternaOutputDto:
        CandidatarNaVagaExternaInputValidator.validar(input_dto)

        curriculo_original = (
            input_dto.curriculo_pre_montado
            if input_dto.curriculo_pre_montado is not None
            else self._extrator.extrair(input_dto.pdf_curriculo)
        )
        analise_vaga = self._analisador_vaga.analisar(input_dto.vaga.descricao)
        curriculo_adaptado = self._ajustar_todas_as_secoes(curriculo_original, input_dto, analise_vaga)
        pdf_bytes = self._gerador_pdf.gerar(curriculo_adaptado, input_dto.idioma_alvo)

        nome_arquivo = NomeArquivo.criar(
            nome_completo=curriculo_original.nome_completo,
            cargo=input_dto.cargo_alvo,
            empresa=input_dto.empresa_alvo,
            data=input_dto.data_referencia,
        )

        resultado_ats = self._calcular_ats_score.executar(curriculo_adaptado, analise_vaga)
        carta_apresentacao = self._gerador_carta.gerar(curriculo_adaptado, analise_vaga, input_dto.idioma_alvo)

        return CandidatarNaVagaExternaOutputDto(
            pdf_bytes=pdf_bytes,
            nome_arquivo=nome_arquivo,
            resultado_ats=resultado_ats,
            carta_apresentacao=carta_apresentacao,
            url_vaga=input_dto.vaga.url,
        )

    def _ajustar_todas_as_secoes(
        self,
        curriculo: Curriculo,
        input_dto: CandidatarNaVagaExternaInputDto,
        analise_vaga: AnaliseVaga,
    ) -> Curriculo:
        contexto = ContextoVaga(
            descricao_vaga=input_dto.vaga.descricao,
            idioma_alvo=input_dto.idioma_alvo,
            analise_vaga=analise_vaga,
            cargo_alvo=input_dto.cargo_alvo,
        )
        curriculo_atualizado = curriculo
        for secao_original in curriculo.secoes:
            secao_ajustada = self._ajustador_texto.ajustar_secao(secao=secao_original, contexto=contexto)
            curriculo_atualizado = curriculo_atualizado.substituir_secao(secao_ajustada)
        return curriculo_atualizado
