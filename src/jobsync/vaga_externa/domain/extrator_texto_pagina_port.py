"""Porta para extração de texto principal de uma página web."""
from __future__ import annotations

from abc import ABC, abstractmethod


class ExtratorTextoPaginaPort(ABC):
    """Usada pelo BuscadorGoogleCustomSearch para obter a descrição completa da vaga."""

    @abstractmethod
    def extrair(self, url: str) -> str | None:
        """Busca a página e extrai o texto principal.

        Retorna `None` se a extração falhar (rede, bloqueio de bot, JS
        obrigatório) — o chamador deve cair para o snippet original nesse caso.
        """
        raise NotImplementedError
