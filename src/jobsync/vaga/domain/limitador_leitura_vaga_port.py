"""Porta para limitar a quantidade de leituras de vaga por pessoa."""

from __future__ import annotations

from abc import ABC, abstractmethod


class LimitadorLeituraVagaPort(ABC):
    """Controla quantas leituras de vaga uma pessoa pode fazer em um período."""

    @abstractmethod
    def registrar(self, usuario_id: str) -> None:
        """Registra uma leitura.

        Levanta `LimiteLeituraVagaExcedido` quando o limite foi atingido.
        """
        raise NotImplementedError
