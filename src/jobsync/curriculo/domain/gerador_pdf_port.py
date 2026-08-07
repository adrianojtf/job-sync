"""Porta (Port) para geração do arquivo PDF final a partir do Curriculo adaptado."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from jobsync.curriculo import Curriculo


class GeradorPdfPort(ABC):
    """Gera os bytes de um PDF formatado a partir de um Curriculo."""

    @abstractmethod
    def gerar(self, curriculo: Curriculo, idioma_alvo: str) -> bytes:
        raise NotImplementedError
