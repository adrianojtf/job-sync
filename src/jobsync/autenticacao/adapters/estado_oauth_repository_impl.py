"""Implementação PostgreSQL de EstadoOAuthRepository."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from psycopg_pool import ConnectionPool

from jobsync.autenticacao.domain.estado_oauth import EstadoOAuth
from jobsync.autenticacao.domain.estado_oauth_repository import EstadoOAuthRepository


class EstadoOAuthRepositoryImpl(EstadoOAuthRepository):
    def __init__(self, pool: ConnectionPool) -> None:
        self._pool = pool

    def salvar(self, estado: EstadoOAuth) -> None:
        with self._pool.connection() as conexao:
            conexao.execute(
                "INSERT INTO estado_oauth (estado_hash, provedor, code_verifier, nonce, destino, expira_em)"
                " VALUES (%s, %s, %s, %s, %s, %s)",
                (
                    estado.estado_hash,
                    estado.provedor,
                    estado.code_verifier,
                    estado.nonce,
                    estado.destino,
                    estado.expira_em,
                ),
            )

    def consumir(self, estado_hash: bytes, agora: datetime) -> Optional[EstadoOAuth]:
        with self._pool.connection() as conexao:
            linha = conexao.execute(
                "DELETE FROM estado_oauth WHERE estado_hash = %s"
                " RETURNING estado_hash, provedor, code_verifier, nonce, destino, expira_em",
                (estado_hash,),
            ).fetchone()
        if linha is None:
            return None
        estado = EstadoOAuth(bytes(linha[0]), linha[1], linha[2], linha[3], linha[4], linha[5])
        return None if estado.expirado(agora) else estado
