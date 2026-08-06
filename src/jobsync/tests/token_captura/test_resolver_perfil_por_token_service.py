"""Testes do caso de uso ResolverPerfilPorToken."""

from jobsync.token_captura import TokenCapturaRepository
from jobsync.token_captura.domain.token_captura import TokenCaptura
from jobsync.token_captura.service_layer.resolver_perfil_por_token import ResolverPerfilPorToken


class TokenCapturaRepositoryFake(TokenCapturaRepository):
    def __init__(self) -> None:
        self._tokens: dict[str, str] = {}

    def criar(self, perfil_identificador: str) -> TokenCaptura:
        token = TokenCaptura(token=f"token-{len(self._tokens) + 1}", perfil_identificador=perfil_identificador)
        self._tokens[token.token] = perfil_identificador
        return token

    def resolver_perfil_por_token(self, token: str) -> str | None:
        return self._tokens.get(token)


class TestResolverPerfilPorToken:
    def test_resolve_perfil_via_repositorio(self):
        repositorio = TokenCapturaRepositoryFake()
        token = repositorio.criar("matheus")
        caso_de_uso = ResolverPerfilPorToken(_repositorio=repositorio)

        perfil = caso_de_uso.executar(token.token)

        assert perfil == "matheus"

    def test_retorna_none_para_token_inexistente(self):
        repositorio = TokenCapturaRepositoryFake()
        caso_de_uso = ResolverPerfilPorToken(_repositorio=repositorio)

        assert caso_de_uso.executar("token-inexistente") is None
