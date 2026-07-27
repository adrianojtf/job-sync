"""Porta para análise de descrições de vagas."""

from abc import ABC, abstractmethod

from domain.analise_vaga import AnaliseVaga


class JobDescriptionAnalyzerPort(ABC):
    """Interface da porta de aplicação para analisar descrições de vagas."""

    @abstractmethod
    def analisar(self, descricao_vaga: str) -> AnaliseVaga:
        """Analisa a descrição da vaga e retorna um modelo de domínio.

        A implementação concreta deve extrair os requisitos técnicos e identificar
        trechos ambíguos, preservando sempre o texto original para auditoria.
        """
        raise NotImplementedError
