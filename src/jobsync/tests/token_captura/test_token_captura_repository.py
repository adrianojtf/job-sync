"""Testes de porta para o repositório de tokens de captura."""

from typing import Optional

from jobsync.token_captura import TokenCaptura, TokenCapturaRepository


class TokenCapturaRepositoryFake(TokenCapturaRepository):
    def __init__(self) -> None:
        self._tokens: dict[str, str] = {}

    def criar(self, perfil_identificador: str) -> TokenCaptura:
        token = TokenCaptura(token=f"token-{len(self._tokens) + 1}", perfil_identificador=perfil_identificador)
        self._tokens[token.token] = perfil_identificador
        return token

    def resolver_perfil_por_token(self, token: str) -> Optional[str]:
        return self._tokens.get(token)


def test_token_captura_repository_eh_interface_pura() -> None:
    fake = TokenCapturaRepositoryFake()

    token = fake.criar("matheus")

    assert fake.resolver_perfil_por_token(token.token) == "matheus"
    assert fake.resolver_perfil_por_token("token-inexistente") is None
