"""Implementação PostgreSQL de PerfilRepository."""
from __future__ import annotations

from typing import Optional

from psycopg_pool import ConnectionPool

from jobsync.perfil.domain.perfil import Perfil
from jobsync.perfil.domain.perfil_repository import PerfilRepository


class PerfilRepositoryImpl(PerfilRepository):
    """Implementação PostgreSQL da porta de perfil."""

    def __init__(self, pool: ConnectionPool) -> None:
        self._pool = pool

    def buscar_por_identificador(self, identificador: str) -> Optional[Perfil]:
        with self._pool.connection() as conexao:
            linha = conexao.execute(
                "SELECT identificador FROM perfil WHERE identificador = %s",
                (identificador,),
            ).fetchone()
        if linha is None:
            return None
        return Perfil(identificador=linha[0])

    def criar(self, identificador: str) -> Perfil:
        perfil = Perfil(identificador=identificador)
        with self._pool.connection() as conexao:
            conexao.execute(
                "INSERT INTO perfil (identificador) VALUES (%s)",
                (perfil.identificador,),
            )
        return perfil
