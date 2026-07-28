"""Caso de uso: adaptar um currículo (PDF) para uma vaga específica, em um idioma alvo.

Orquestra as três portas (extração, ajuste de texto por seção, geração de PDF)
sem conhecer os detalhes de infraestrutura de cada uma (Dependency Inversion).
Cada seção do currículo é ajustada de forma independente, conforme solicitado:
TECHNICAL SKILLS (Tecnologias), Perfil, Experiências e Formação são lidos e
reescritos separadamente antes de serem remontados no currículo final.
"""
from __future__ import annotations

from application.use_cases.adaptar_curriculo_para_vaga.dtos import (
    AdaptarCurriculoParaVagaInputDto,
    AdaptarCurriculoParaVagaOutputDto,
)
from application.use_cases.adaptar_curriculo_para_vaga.validator import (
    AdaptarCurriculoParaVagaInputValidator,
)
from domain.curriculo import Curriculo
from domain.curriculo.ajustador_texto_port import AjustadorTextoPort
from domain.curriculo.extrator_curriculo_port import ExtratorCurriculoPort
from domain.curriculo.gerador_pdf_port import GeradorPdfPort
from domain.nome_arquivo import NomeArquivo
from domain.vaga import AnaliseVaga
from domain.vaga.job_description_analyzer_port import JobDescriptionAnalyzerPort


class AdaptarCurriculoParaVaga:
    """Caso de uso principal do sistema: lê o PDF, ajusta cada seção via IA e gera o PDF final."""

    def __init__(
        self,
        extrator: ExtratorCurriculoPort,
        analisador_vaga: JobDescriptionAnalyzerPort,
        ajustador_texto: AjustadorTextoPort,
        gerador_pdf: GeradorPdfPort,
    ) -> None:
        self._extrator = extrator
        self._analisador_vaga = analisador_vaga
        self._ajustador_texto = ajustador_texto
        self._gerador_pdf = gerador_pdf

    def executar(self, input_dto: AdaptarCurriculoParaVagaInputDto) -> AdaptarCurriculoParaVagaOutputDto:
        AdaptarCurriculoParaVagaInputValidator.validar(input_dto)

        curriculo_original = (
            input_dto.curriculo_pre_montado
            if input_dto.curriculo_pre_montado is not None
            else self._extrator.extrair(input_dto.pdf_curriculo)
        )
        analise_vaga = self._analisador_vaga.analisar(input_dto.descricao_vaga)
        curriculo_adaptado = self._ajustar_todas_as_secoes(curriculo_original, input_dto, analise_vaga)
        pdf_bytes = self._gerador_pdf.gerar(curriculo_adaptado, input_dto.idioma_alvo)

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
        )

    def _ajustar_todas_as_secoes(
        self,
        curriculo: Curriculo,
        input_dto: AdaptarCurriculoParaVagaInputDto,
        analise_vaga: AnaliseVaga,
    ) -> Curriculo:
        curriculo_atualizado = curriculo
        for secao_original in curriculo.secoes:
            secao_ajustada = self._ajustador_texto.ajustar_secao(
                secao=secao_original,
                descricao_vaga=input_dto.descricao_vaga,
                idioma_alvo=input_dto.idioma_alvo,
                analise_vaga=analise_vaga,
            )
            curriculo_atualizado = curriculo_atualizado.substituir_secao(secao_ajustada)
        return curriculo_atualizado
