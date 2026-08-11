"""Implementação em memória (fake) de TokenCapturaRepository para testes."""

from __future__ import annotations

import secrets
from typing import Optional

from jobsync.token_captura.domain.token_captura import TokenCaptura
from jobsync.token_captura.domain.token_captura_repository import TokenCapturaRepository


class TokenCapturaRepositoryFake(TokenCapturaRepository):
    """Fake em memória para testes de API e serviços."""

    def __init__(self) -> None:
        self._tokens: dict[str, str] = {}

    def criar(self, perfil_identificador: str) -> TokenCaptura:
        token = secrets.token_urlsafe(32)
        self._tokens[token] = perfil_identificador
        return TokenCaptura(token=token, perfil_identificador=perfil_identificador)

    def resolver_perfil_por_token(self, token: str) -> Optional[str]:
        return self._tokens.get(token)
