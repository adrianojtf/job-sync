"""Implementação PostgreSQL de TokenUsoUnicoRepository."""
from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from psycopg_pool import ConnectionPool

from jobsync.autenticacao.domain.token_uso_unico import Finalidade, TokenUsoUnico
from jobsync.autenticacao.domain.token_uso_unico_repository import TokenUsoUnicoRepository


class TokenUsoUnicoRepositoryImpl(TokenUsoUnicoRepository):
    def __init__(self, pool: ConnectionPool) -> None:
        self._pool = pool

    def salvar(self, token: TokenUsoUnico) -> None:
        with self._pool.connection() as conexao:
            conexao.execute(
                "INSERT INTO token_uso_unico (token_hash, usuario_id, finalidade, expira_em, usado_em)"
                " VALUES (%s, %s, %s, %s, %s)",
                (token.token_hash, token.usuario_id, token.finalidade.value, token.expira_em, token.usado_em),
            )

    def consumir(
        self, token_hash: bytes, finalidade: Finalidade, agora: datetime
    ) -> Optional[TokenUsoUnico]:
        with self._pool.connection() as conexao:
            linha = conexao.execute(
                "UPDATE token_uso_unico SET usado_em = %s"
                " WHERE token_hash = %s AND finalidade = %s AND usado_em IS NULL AND expira_em > %s"
                " RETURNING token_hash, usuario_id, finalidade, expira_em, usado_em",
                (agora, token_hash, finalidade.value, agora),
            ).fetchone()
        if linha is None:
            return None
        return TokenUsoUnico(bytes(linha[0]), linha[1], Finalidade(linha[2]), linha[3], linha[4])

    def remover_do_usuario(self, usuario_id: UUID, finalidade: Finalidade) -> None:
        with self._pool.connection() as conexao:
            conexao.execute(
                "DELETE FROM token_uso_unico WHERE usuario_id = %s AND finalidade = %s",
                (usuario_id, finalidade.value),
            )
