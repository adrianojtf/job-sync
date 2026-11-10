"""Porta de persistência de tokens de uso único."""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from uuid import UUID

from jobsync.autenticacao.domain.token_uso_unico import Finalidade, TokenUsoUnico


class TokenUsoUnicoRepository(ABC):
    @abstractmethod
    def salvar(self, token: TokenUsoUnico) -> None: ...

    @abstractmethod
    def consumir(
        self, token_hash: bytes, finalidade: Finalidade, agora: datetime
    ) -> Optional[TokenUsoUnico]:
        """Marca o token como usado e o devolve, de forma atômica.

        Devolve `None` se o token não existe, já foi usado, expirou ou tem outra finalidade.
        """

    @abstractmethod
    def remover_do_usuario(self, usuario_id: UUID, finalidade: Finalidade) -> None: ...
