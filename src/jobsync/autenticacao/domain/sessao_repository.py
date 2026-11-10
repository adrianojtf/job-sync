"""Porta de persistência de sessões."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from jobsync.autenticacao.domain.sessao import Sessao


class SessaoRepository(ABC):
    """Contrato de acesso às sessões, sempre identificadas pelo hash do token."""

    @abstractmethod
    def salvar(self, sessao: Sessao) -> None: ...

    @abstractmethod
    def buscar(self, token_hash: bytes) -> Optional[Sessao]: ...

    @abstractmethod
    def atualizar(self, sessao: Sessao) -> None: ...

    @abstractmethod
    def remover(self, token_hash: bytes) -> None: ...

    @abstractmethod
    def remover_todas_do_usuario(self, usuario_id: UUID) -> None: ...
