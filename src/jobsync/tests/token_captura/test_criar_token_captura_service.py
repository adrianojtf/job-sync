"""Testes do caso de uso CriarTokenCaptura."""

from jobsync.token_captura import TokenCapturaRepository
from jobsync.token_captura.domain.token_captura import TokenCaptura
from jobsync.token_captura.service_layer.criar_token_captura import CriarTokenCaptura


class TokenCapturaRepositoryFake(TokenCapturaRepository):
    def __init__(self) -> None:
        self._tokens: dict[str, str] = {}

    def criar(self, perfil_identificador: str) -> TokenCaptura:
        token = TokenCaptura(token=f"token-{len(self._tokens) + 1}", perfil_identificador=perfil_identificador)
        self._tokens[token.token] = perfil_identificador
        return token

    def resolver_perfil_por_token(self, token: str) -> str | None:
        return self._tokens.get(token)


class TestCriarTokenCaptura:
    def test_cria_token_via_repositorio(self):
        repositorio = TokenCapturaRepositoryFake()
        caso_de_uso = CriarTokenCaptura(_repositorio=repositorio)

        token = caso_de_uso.executar("matheus")

        assert token.perfil_identificador == "matheus"
