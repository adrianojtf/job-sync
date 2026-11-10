"""Testes dos serviços ResolverSessao e EncerrarSessao."""

from datetime import timedelta

import pytest

from jobsync.autenticacao.domain.email import Email
from jobsync.autenticacao.domain.token_opaco import hash_token
from jobsync.autenticacao.domain.usuario import Usuario
from jobsync.autenticacao.service_layer.emitir_sessao.service import EmitirSessao
from jobsync.autenticacao.service_layer.encerrar_sessao.service import EncerrarSessao
from jobsync.autenticacao.service_layer.resolver_sessao.service import ResolverSessao


@pytest.fixture
def usuario(ambiente):
    novo = Usuario.novo(Email("ana@exemplo.com"), "u-aaaaaaaaaaaa", ambiente.relogio.agora).verificar_email()
    ambiente.usuarios.salvar_novo(novo)
    return novo


@pytest.fixture
def token(ambiente, usuario):
    return EmitirSessao(ambiente.sessoes, ambiente.config, ambiente.relogio).executar(usuario.id)


@pytest.fixture
def resolver(ambiente):
    return ResolverSessao(ambiente.usuarios, ambiente.sessoes, ambiente.config, ambiente.relogio)


class TestResolverSessao:
    def test_devolve_o_usuario_da_sessao_valida(self, resolver, usuario, token):
        assert resolver.executar(token) == usuario

    @pytest.mark.parametrize("token_invalido", [None, "", "token-que-nao-existe"])
    def test_token_ausente_ou_desconhecido_devolve_none(self, resolver, token_invalido):
        assert resolver.executar(token_invalido) is None

    def test_sessao_expira_por_inatividade_e_e_removida(self, ambiente, resolver, token):
        ambiente.relogio.avancar(days=7)

        assert resolver.executar(token) is None
        assert ambiente.sessoes.buscar(hash_token(token)) is None

    def test_sessao_expira_no_limite_absoluto_mesmo_com_uso_continuo(self, ambiente, resolver, token):
        for _ in range(30):
            ambiente.relogio.avancar(days=1)
            resolver.executar(token)

        assert resolver.executar(token) is None

    def test_uso_renova_o_ultimo_acesso_apos_o_intervalo_minimo(self, ambiente, resolver, token):
        ambiente.relogio.avancar(minutes=6)

        resolver.executar(token)

        assert ambiente.sessoes.buscar(hash_token(token)).ultimo_acesso_em == ambiente.relogio.agora

    def test_nao_renova_antes_do_intervalo_minimo(self, ambiente, resolver, token):
        inicial = ambiente.relogio.agora
        ambiente.relogio.avancar(minutes=1)

        resolver.executar(token)

        assert ambiente.sessoes.buscar(hash_token(token)).ultimo_acesso_em == inicial

    def test_sessao_de_usuario_removido_devolve_none(self, ambiente, resolver, token):
        ambiente.usuarios = type(ambiente.usuarios)()
        resolver = ResolverSessao(ambiente.usuarios, ambiente.sessoes, ambiente.config, ambiente.relogio)

        assert resolver.executar(token) is None
        assert ambiente.sessoes.buscar(hash_token(token)) is None


class TestEncerrarSessao:
    def test_remove_a_sessao(self, ambiente, resolver, token):
        EncerrarSessao(ambiente.sessoes).executar(token)

        assert resolver.executar(token) is None

    def test_token_desconhecido_ou_ausente_nao_gera_erro(self, ambiente):
        servico = EncerrarSessao(ambiente.sessoes)

        servico.executar("desconhecido")
        servico.executar(None)
