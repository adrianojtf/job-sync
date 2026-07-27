"""Porta (Port) de entrada para extração de currículo a partir de um arquivo PDF.

Qualquer adapter que implemente esta interface pode ser plugado ao caso de
uso sem alterar a lógica de aplicação (Dependency Inversion Principle).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from domain.curriculo import Curriculo


class ExtratorCurriculoPort(ABC):
    """Extrai um objeto de domínio Curriculo a partir dos bytes de um PDF."""

    @abstractmethod
    def extrair(self, conteudo_pdf: bytes) -> Curriculo:
        """Analisa o PDF e retorna um Curriculo estruturado em seções.

        Levanta ValueError se o PDF não puder ser interpretado como currículo.
        """
        raise NotImplementedError
