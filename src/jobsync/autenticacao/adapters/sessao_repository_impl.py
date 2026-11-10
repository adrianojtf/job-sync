"""Implementação PostgreSQL de SessaoRepository."""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from psycopg_pool import ConnectionPool

from jobsync.autenticacao.domain.sessao import Sessao
from jobsync.autenticacao.domain.sessao_repository import SessaoRepository


class SessaoRepositoryImpl(SessaoRepository):
    def __init__(self, pool: ConnectionPool) -> None:
        self._pool = pool

    def salvar(self, sessao: Sessao) -> None:
        with self._pool.connection() as conexao:
            conexao.execute(
                "INSERT INTO sessao (token_hash, usuario_id, criada_em, ultimo_acesso_em, expira_em)"
                " VALUES (%s, %s, %s, %s, %s)",
                (
                    sessao.token_hash,
                    sessao.usuario_id,
                    sessao.criada_em,
                    sessao.ultimo_acesso_em,
                    sessao.expira_em,
                ),
            )

    def buscar(self, token_hash: bytes) -> Optional[Sessao]:
        with self._pool.connection() as conexao:
            linha = conexao.execute(
                "SELECT token_hash, usuario_id, criada_em, ultimo_acesso_em, expira_em"
                " FROM sessao WHERE token_hash = %s",
                (token_hash,),
            ).fetchone()
        if linha is None:
            return None
        return Sessao(bytes(linha[0]), linha[1], linha[2], linha[3], linha[4])

    def atualizar(self, sessao: Sessao) -> None:
        with self._pool.connection() as conexao:
            conexao.execute(
                "UPDATE sessao SET ultimo_acesso_em = %s WHERE token_hash = %s",
                (sessao.ultimo_acesso_em, sessao.token_hash),
            )

    def remover(self, token_hash: bytes) -> None:
        with self._pool.connection() as conexao:
            conexao.execute("DELETE FROM sessao WHERE token_hash = %s", (token_hash,))

    def remover_todas_do_usuario(self, usuario_id: UUID) -> None:
        with self._pool.connection() as conexao:
            conexao.execute("DELETE FROM sessao WHERE usuario_id = %s", (usuario_id,))
