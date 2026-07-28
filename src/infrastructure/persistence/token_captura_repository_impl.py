"""Implementação SQLite de TokenCapturaRepository."""
from __future__ import annotations

import uuid
from typing import Optional

from domain.token_captura import TokenCaptura
from domain.token_captura.token_captura_repository import TokenCapturaRepository
from infrastructure.persistence._conexao_sqlite import criar_conexao


class TokenCapturaRepositoryImpl(TokenCapturaRepository):
    """Implementação SQLite da porta de tokens de captura."""

    def __init__(self, caminho_banco: str) -> None:
        self._conexao = criar_conexao(caminho_banco)

    def criar(self, perfil_identificador: str) -> TokenCaptura:
        token = TokenCaptura(token=str(uuid.uuid4()), perfil_identificador=perfil_identificador)
        self._conexao.execute(
            "INSERT INTO token_captura (token, perfil_identificador) VALUES (?, ?)",
            (token.token, token.perfil_identificador),
        )
        self._conexao.commit()
        return token

    def resolver_perfil_por_token(self, token: str) -> Optional[str]:
        cursor = self._conexao.execute(
            "SELECT perfil_identificador FROM token_captura WHERE token = ?",
            (token,),
        )
        linha = cursor.fetchone()
        return linha[0] if linha is not None else None
