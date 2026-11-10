"""Dublê em memória de EstadoOAuthRepository."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from jobsync.autenticacao.domain.estado_oauth import EstadoOAuth
from jobsync.autenticacao.domain.estado_oauth_repository import EstadoOAuthRepository


class EstadoOAuthRepositoryFake(EstadoOAuthRepository):
    def __init__(self) -> None:
        self._estados: dict[bytes, EstadoOAuth] = {}

    def salvar(self, estado: EstadoOAuth) -> None:
        self._estados[estado.estado_hash] = estado

    def consumir(self, estado_hash: bytes, agora: datetime) -> Optional[EstadoOAuth]:
        estado = self._estados.pop(estado_hash, None)
        if estado is None or estado.expirado(agora):
            return None
        return estado
