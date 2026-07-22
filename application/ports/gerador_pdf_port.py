"""Porta (Port) para geração do arquivo PDF final a partir do Curriculo adaptado."""
from abc import ABC, abstractmethod

from domain.curriculo import Curriculo


class GeradorPdfPort(ABC):
    """Gera os bytes de um PDF formatado a partir de um Curriculo."""

    @abstractmethod
    def gerar(self, curriculo: Curriculo) -> bytes:
        raise NotImplementedError
