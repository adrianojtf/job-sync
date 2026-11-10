"""Porta de persistência do limite de tentativas de login."""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from jobsync.autenticacao.domain.limite_tentativa import LimiteTentativa, PoliticaLimiteTentativas


class LimiteTentativasRepository(ABC):
    @abstractmethod
    def obter(self, chave: str) -> Optional[LimiteTentativa]: ...

    @abstractmethod
    def registrar_falha(
        self, chave: str, agora: datetime, politica: PoliticaLimiteTentativas
    ) -> LimiteTentativa:
        """Registra uma falha de forma atômica, mesmo com requisições concorrentes."""

    @abstractmethod
    def limpar(self, chave: str) -> None: ...
