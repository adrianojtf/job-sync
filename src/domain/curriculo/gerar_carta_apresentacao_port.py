"""Porta (Port) para geração de carta de apresentação personalizada."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from domain.curriculo import Curriculo
    from domain.vaga import AnaliseVaga


class GerarCartaApresentacaoPort(ABC):
    """Interface da porta de aplicação para gerar o texto de uma carta de apresentação."""

    @abstractmethod
    def gerar(self, curriculo: Curriculo, analise_vaga: AnaliseVaga, idioma_alvo: str) -> str:
        """Gera o texto da carta de apresentação personalizada para a vaga e o currículo.

        A implementação concreta deve preservar os fatos do currículo original,
        sem inventar experiências, tecnologias ou resultados não presentes nele.
        """
        raise NotImplementedError
