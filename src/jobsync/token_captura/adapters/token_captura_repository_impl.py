"""Implementação PostgreSQL de TokenCapturaRepository."""
from __future__ import annotations

import uuid
from typing import Optional

from psycopg_pool import ConnectionPool

from jobsync.token_captura.domain.token_captura import TokenCaptura
from jobsync.token_captura.domain.token_captura_repository import TokenCapturaRepository


class TokenCapturaRepositoryImpl(TokenCapturaRepository):
    """Implementação PostgreSQL da porta de tokens de captura."""

    def __init__(self, pool: ConnectionPool) -> None:
        self._pool = pool

    def criar(self, perfil_identificador: str) -> TokenCaptura:
        token = TokenCaptura(token=str(uuid.uuid4()), perfil_identificador=perfil_identificador)
        with self._pool.connection() as conexao:
            conexao.execute(
                "INSERT INTO token_captura (token, perfil_identificador) VALUES (%s, %s)",
                (token.token, token.perfil_identificador),
            )
        return token

    def resolver_perfil_por_token(self, token: str) -> Optional[str]:
        with self._pool.connection() as conexao:
            linha = conexao.execute(
                "SELECT perfil_identificador FROM token_captura WHERE token = %s",
                (token,),
            ).fetchone()
        return linha[0] if linha is not None else None
