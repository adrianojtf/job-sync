"""Implementação SQLite de PerfilRepository."""
from __future__ import annotations

from typing import Optional

from infrastructure.persistence._conexao_sqlite import criar_conexao

from jobsync.perfil.domain.perfil import Perfil
from jobsync.perfil.domain.perfil_repository import PerfilRepository


class PerfilRepositoryImpl(PerfilRepository):
    """Implementação SQLite da porta de perfil."""

    def __init__(self, caminho_banco: str) -> None:
        self._conexao = criar_conexao(caminho_banco)

    def buscar_por_identificador(self, identificador: str) -> Optional[Perfil]:
        cursor = self._conexao.execute(
            "SELECT identificador FROM perfil WHERE identificador = ?",
            (identificador,),
        )
        linha = cursor.fetchone()
        if linha is None:
            return None
        return Perfil(identificador=linha[0])

    def criar(self, identificador: str) -> Perfil:
        perfil = Perfil(identificador=identificador)
        self._conexao.execute(
            "INSERT INTO perfil (identificador) VALUES (?)",
            (perfil.identificador,),
        )
        self._conexao.commit()
        return perfil
