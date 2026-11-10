"""Testes dos serviços SolicitarRedefinicaoSenha e RedefinirSenha."""

from datetime import timedelta

import pytest

from jobsync.autenticacao.domain.email import Email
from jobsync.autenticacao.domain.exceptions import SenhaInvalida, TokenInvalido
from jobsync.autenticacao.domain.token_opaco import hash_token
from jobsync.autenticacao.domain.usuario import Usuario
from jobsync.autenticacao.service_layer.emitir_sessao.service import EmitirSessao
from jobsync.autenticacao.service_layer.redefinir_senha.service import RedefinirSenha
from jobsync.autenticacao.service_layer.solicitar_redefinicao_senha.service import SolicitarRedefinicaoSenha


@pytest.fixture
def solicitar(ambiente):
    return SolicitarRedefinicaoSenha(ambiente.usuarios, ambiente.tokens, ambiente.enviador, ambiente.config, ambiente.relogio)


@pytest.fixture
def redefinir(ambiente):
    return RedefinirSenha(ambiente.usuarios, ambiente.tokens, ambiente.sessoes, ambiente.hasher, ambiente.relogio)


@pytest.fixture
def usuario(ambiente):
    ativo = Usuario.novo(Email("ana@exemplo.com"), "u-aaaaaaaaaaaa", ambiente.relogio.agora).verificar_email()
    ambiente.usuarios.salvar_novo(ativo)
    ambiente.usuarios.definir_senha_hash(ativo.id, ambiente.hasher.gerar("senha-antiga-123"))
    return ativo


class TestSolicitarRedefinicaoSenha:
    def test_envia_link_para_usuario_verificado(self, ambiente, solicitar, usuario):
        solicitar.executar("Ana@Exemplo.com")

        _, _, corpo = ambiente.enviador.para("ana@exemplo.com")[0]
        assert "http://localhost:8080/redefinir-senha?token=" in corpo

    def test_nao_envia_nada_para_email_desconhecido(self, ambiente, solicitar):
        solicitar.executar("ninguem@exemplo.com")

        assert ambiente.enviador.enviados == []

    def test_nao_envia_para_usuario_sem_email_verificado(self, ambiente, solicitar):
        ambiente.usuarios.salvar_novo(Usuario.novo(Email("nova@exemplo.com"), "u-cccccccccccc", ambiente.relogio.agora))

        solicitar.executar("nova@exemplo.com")

        assert ambiente.enviador.enviados == []

    def test_email_malformado_e_ignorado_sem_erro(self, ambiente, solicitar):
        solicitar.executar("isto-nao-e-email")

        assert ambiente.enviador.enviados == []

    def test_novo_pedido_invalida_o_link_anterior(self, ambiente, solicitar, redefinir, usuario):
        solicitar.executar("ana@exemplo.com")
        primeiro = ambiente.enviador.ultimo_token("ana@exemplo.com")

        solicitar.executar("ana@exemplo.com")

        with pytest.raises(TokenInvalido):
            redefinir.executar(primeiro, "nova-senha-longa-1")


class TestRedefinirSenha:
    def test_troca_a_senha(self, ambiente, solicitar, redefinir, usuario):
        solicitar.executar("ana@exemplo.com")
        token = ambiente.enviador.ultimo_token("ana@exemplo.com")

        redefinir.executar(token, "nova-senha-longa-1")

        assert ambiente.usuarios.obter_senha_hash(usuario.id) == ambiente.hasher.gerar("nova-senha-longa-1")

    def test_encerra_todas_as_sessoes_do_usuario(self, ambiente, solicitar, redefinir, usuario):
        emitir = EmitirSessao(ambiente.sessoes, ambiente.config, ambiente.relogio)
        token_sessao = emitir.executar(usuario.id)
        solicitar.executar("ana@exemplo.com")

        redefinir.executar(ambiente.enviador.ultimo_token("ana@exemplo.com"), "nova-senha-longa-1")

        assert ambiente.sessoes.buscar(hash_token(token_sessao)) is None

    def test_cria_a_credencial_quando_o_usuario_so_usava_google(self, ambiente, solicitar, redefinir):
        so_google = Usuario.novo(Email("g@exemplo.com"), "u-dddddddddddd", ambiente.relogio.agora).verificar_email()
        ambiente.usuarios.salvar_novo(so_google)
        solicitar.executar("g@exemplo.com")

        redefinir.executar(ambiente.enviador.ultimo_token("g@exemplo.com"), "nova-senha-longa-1")

        assert ambiente.usuarios.obter_senha_hash(so_google.id) == ambiente.hasher.gerar("nova-senha-longa-1")

    def test_link_so_funciona_uma_vez(self, ambiente, solicitar, redefinir, usuario):
        solicitar.executar("ana@exemplo.com")
        token = ambiente.enviador.ultimo_token("ana@exemplo.com")
        redefinir.executar(token, "nova-senha-longa-1")

        with pytest.raises(TokenInvalido):
            redefinir.executar(token, "outra-senha-longa-2")

    def test_link_expira_em_uma_hora(self, ambiente, solicitar, redefinir, usuario):
        solicitar.executar("ana@exemplo.com")
        token = ambiente.enviador.ultimo_token("ana@exemplo.com")
        ambiente.relogio.avancar(hours=1)

        with pytest.raises(TokenInvalido):
            redefinir.executar(token, "nova-senha-longa-1")

    def test_senha_fraca_e_recusada_sem_consumir_o_link(self, ambiente, solicitar, redefinir, usuario):
        solicitar.executar("ana@exemplo.com")
        token = ambiente.enviador.ultimo_token("ana@exemplo.com")

        with pytest.raises(SenhaInvalida):
            redefinir.executar(token, "curta")

        redefinir.executar(token, "nova-senha-longa-1")
        assert ambiente.usuarios.obter_senha_hash(usuario.id) == ambiente.hasher.gerar("nova-senha-longa-1")

    def test_token_desconhecido_gera_erro(self, redefinir):
        with pytest.raises(TokenInvalido):
            redefinir.executar("nao-existe", "nova-senha-longa-1")
