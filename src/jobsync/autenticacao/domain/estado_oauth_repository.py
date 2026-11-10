"""Porta de persistência do estado temporário do login OAuth."""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from jobsync.autenticacao.domain.estado_oauth import EstadoOAuth


class EstadoOAuthRepository(ABC):
    @abstractmethod
    def salvar(self, estado: EstadoOAuth) -> None: ...

    @abstractmethod
    def consumir(self, estado_hash: bytes, agora: datetime) -> Optional[EstadoOAuth]:
        """Remove o estado e o devolve; devolve `None` se não existe ou já expirou."""
