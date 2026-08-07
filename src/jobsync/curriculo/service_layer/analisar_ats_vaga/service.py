"""Caso de uso: analisar a aderência de ATS de um currículo a uma vaga, sem adaptá-lo.

Diferente de AdaptarCurriculoParaVaga, este caso de uso NÃO reescreve nenhuma
seção do currículo (a etapa mais cara do fluxo de adaptação, pois chama a IA
uma vez por seção) — apenas extrai o currículo original, analisa a vaga,
calcula o ATS Score (Domain Service `CalcularAtsScore`) e sugere o que mudar.
Pensado para quem só quer o diagnóstico rápido, sem gerar um PDF adaptado.
"""
from __future__ import annotations

from jobsync.curriculo.service_layer.analisar_ats_vaga.dtos import (
    AnalisarAtsVagaInputDto,
    AnalisarAtsVagaOutputDto,
)
from jobsync.curriculo.service_layer.analisar_ats_vaga.validator import AnalisarAtsVagaInputValidator
from jobsync.ats_score.domain.calcular_ats_score_service import CalcularAtsScore
from jobsync.curriculo.domain.extrator_curriculo_port import ExtratorCurriculoPort
from jobsync.curriculo.domain.gerar_sugestoes_ats_port import GerarSugestoesAtsPort
from jobsync.vaga.domain.job_description_analyzer_port import JobDescriptionAnalyzerPort


class AnalisarAtsVaga:
    """Diagnostica a aderência de ATS de um currículo a uma vaga, com sugestões de melhoria."""

    def __init__(
        self,
        extrator: ExtratorCurriculoPort,
        analisador_vaga: JobDescriptionAnalyzerPort,
        calcular_ats_score: CalcularAtsScore,
        gerador_sugestoes: GerarSugestoesAtsPort,
    ) -> None:
        self._extrator = extrator
        self._analisador_vaga = analisador_vaga
        self._calcular_ats_score = calcular_ats_score
        self._gerador_sugestoes = gerador_sugestoes

    def executar(self, input_dto: AnalisarAtsVagaInputDto) -> AnalisarAtsVagaOutputDto:
        AnalisarAtsVagaInputValidator.validar(input_dto)

        curriculo = (
            input_dto.curriculo_pre_montado
            if input_dto.curriculo_pre_montado is not None
            else self._extrator.extrair(input_dto.pdf_curriculo)
        )
        analise_vaga = self._analisador_vaga.analisar(input_dto.descricao_vaga)
        resultado_ats = self._calcular_ats_score.executar(curriculo, analise_vaga)
        sugestoes = self._gerador_sugestoes.gerar(curriculo, analise_vaga, resultado_ats)

        return AnalisarAtsVagaOutputDto(
            curriculo=curriculo,
            analise_vaga=analise_vaga,
            resultado_ats=resultado_ats,
            sugestoes=sugestoes,
        )
