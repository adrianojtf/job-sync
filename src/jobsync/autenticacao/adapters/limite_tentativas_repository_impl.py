"""Implementação PostgreSQL de LimiteTentativasRepository."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from psycopg_pool import ConnectionPool

from jobsync.autenticacao.domain.limite_tentativa import LimiteTentativa, PoliticaLimiteTentativas
from jobsync.autenticacao.domain.limite_tentativas_repository import LimiteTentativasRepository

_COLUNAS = "chave, contagem, janela_inicia_em, bloqueado_ate"


class LimiteTentativasRepositoryImpl(LimiteTentativasRepository):
    def __init__(self, pool: ConnectionPool) -> None:
        self._pool = pool

    def obter(self, chave: str) -> Optional[LimiteTentativa]:
        with self._pool.connection() as conexao:
            linha = conexao.execute(
                f"SELECT {_COLUNAS} FROM limite_tentativa WHERE chave = %s", (chave,)
            ).fetchone()
        return LimiteTentativa(*linha) if linha else None

    def registrar_falha(
        self, chave: str, agora: datetime, politica: PoliticaLimiteTentativas
    ) -> LimiteTentativa:
        with self._pool.connection() as conexao:
            conexao.execute(
                "INSERT INTO limite_tentativa (chave, contagem, janela_inicia_em) VALUES (%s, 0, %s)"
                " ON CONFLICT (chave) DO NOTHING",
                (chave, agora),
            )
            linha = conexao.execute(
                f"SELECT {_COLUNAS} FROM limite_tentativa WHERE chave = %s FOR UPDATE", (chave,)
            ).fetchone()
            atualizado = LimiteTentativa(*linha).registrar_falha(agora, politica)
            conexao.execute(
                "UPDATE limite_tentativa SET contagem = %s, janela_inicia_em = %s, bloqueado_ate = %s"
                " WHERE chave = %s",
                (atualizado.contagem, atualizado.janela_inicia_em, atualizado.bloqueado_ate, chave),
            )
        return atualizado

    def limpar(self, chave: str) -> None:
        with self._pool.connection() as conexao:
            conexao.execute("DELETE FROM limite_tentativa WHERE chave = %s", (chave,))
