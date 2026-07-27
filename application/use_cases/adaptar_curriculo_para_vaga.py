"""Caso de uso: adaptar um currículo (PDF) para uma vaga específica, em um idioma alvo.

Orquestra as três portas (extração, ajuste de texto por seção, geração de PDF)
sem conhecer os detalhes de infraestrutura de cada uma (Dependency Inversion).
Cada seção do currículo é ajustada de forma independente, conforme solicitado:
TECHNICAL SKILLS (Tecnologias), Perfil, Experiências e Formação são lidos e
reescritos separadamente antes de serem remontados no currículo final.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from application.ports.ajustador_texto_port import AjustadorTextoPort
from application.ports.extrator_curriculo_port import ExtratorCurriculoPort
from application.ports.gerador_pdf_port import GeradorPdfPort
from application.ports.job_description_analyzer_port import JobDescriptionAnalyzerPort
from domain.analise_vaga import AnaliseVaga
from domain.curriculo import Curriculo
from domain.nome_arquivo import NomeArquivo

IDIOMAS_SUPORTADOS = {"pt", "en"}


@dataclass(frozen=True)
class SolicitacaoAdaptacao:
    """Dados de entrada do caso de uso, vindos da interface (Streamlit)."""

    pdf_curriculo: bytes
    descricao_vaga: str
    idioma_alvo: str
    cargo_alvo: str
    empresa_alvo: str
    data_referencia: date | None = None


@dataclass(frozen=True)
class ResultadoAdaptacao:
    """Resultado do caso de uso: PDF gerado e nome de arquivo padronizado."""

    pdf_bytes: bytes
    nome_arquivo: NomeArquivo
    curriculo_adaptado: Curriculo


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

    def executar(self, solicitacao: SolicitacaoAdaptacao) -> ResultadoAdaptacao:
        self._validar(solicitacao)

        curriculo_original = self._extrator.extrair(solicitacao.pdf_curriculo)
        analise_vaga = self._analisador_vaga.analisar(solicitacao.descricao_vaga)
        curriculo_adaptado = self._ajustar_todas_as_secoes(curriculo_original, solicitacao, analise_vaga)
        pdf_bytes = self._gerador_pdf.gerar(curriculo_adaptado, solicitacao.idioma_alvo)

        nome_arquivo = NomeArquivo.criar(
            nome_completo=curriculo_original.nome_completo,
            cargo=solicitacao.cargo_alvo,
            empresa=solicitacao.empresa_alvo,
            data=solicitacao.data_referencia,
        )

        return ResultadoAdaptacao(
            pdf_bytes=pdf_bytes,
            nome_arquivo=nome_arquivo,
            curriculo_adaptado=curriculo_adaptado,
        )

    def _ajustar_todas_as_secoes(
        self,
        curriculo: Curriculo,
        solicitacao: SolicitacaoAdaptacao,
        analise_vaga: AnaliseVaga,
    ) -> Curriculo:
        curriculo_atualizado = curriculo
        for secao_original in curriculo.secoes:
            secao_ajustada = self._ajustador_texto.ajustar_secao(
                secao=secao_original,
                descricao_vaga=solicitacao.descricao_vaga,
                idioma_alvo=solicitacao.idioma_alvo,
                analise_vaga=analise_vaga,
            )
            curriculo_atualizado = curriculo_atualizado.substituir_secao(secao_ajustada)
        return curriculo_atualizado

    @staticmethod
    def _validar(solicitacao: SolicitacaoAdaptacao) -> None:
        if solicitacao.idioma_alvo not in IDIOMAS_SUPORTADOS:
            raise ValueError(
                f"idioma alvo inválido: '{solicitacao.idioma_alvo}'. "
                f"Idiomas suportados: {sorted(IDIOMAS_SUPORTADOS)}"
            )
        if not solicitacao.descricao_vaga or not solicitacao.descricao_vaga.strip():
            raise ValueError("A descrição da vaga é obrigatória.")
        if not solicitacao.pdf_curriculo:
            raise ValueError("O PDF do currículo é obrigatório.")
