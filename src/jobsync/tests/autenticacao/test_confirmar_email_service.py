"""Testes do serviço ConfirmarEmail."""

from datetime import timedelta

import pytest

from jobsync.autenticacao.domain.email import Email
from jobsync.autenticacao.domain.exceptions import TokenInvalido
from jobsync.autenticacao.service_layer.cadastrar_usuario.service import CadastrarUsuario
from jobsync.autenticacao.service_layer.confirmar_email.service import ConfirmarEmail

SENHA = "uma-senha-longa-1"


def _cadastrar(ambiente, email="ana@exemplo.com", senha=SENHA):
    CadastrarUsuario(
        ambiente.usuarios, ambiente.tokens, ambiente.hasher, ambiente.enviador, ambiente.config, ambiente.relogio
    ).executar(email, senha)
    return ambiente.enviador.ultimo_token(email)


def _confirmar(ambiente, token):
    ConfirmarEmail(ambiente.usuarios, ambiente.tokens, ambiente.relogio).executar(token)


class TestConfirmarEmail:
    def test_verifica_o_email_e_ativa_a_senha_escolhida(self, ambiente):
        token = _cadastrar(ambiente)

        _confirmar(ambiente, token)

        usuario = ambiente.usuarios.buscar_por_email(Email("ana@exemplo.com"))
        assert usuario.email_verificado is True
        assert ambiente.usuarios.obter_senha_hash(usuario.id) == ambiente.hasher.gerar(SENHA)

    def test_token_so_funciona_uma_vez(self, ambiente):
        token = _cadastrar(ambiente)
        _confirmar(ambiente, token)

        with pytest.raises(TokenInvalido):
            _confirmar(ambiente, token)

    def test_token_expirado_gera_erro(self, ambiente):
        token = _cadastrar(ambiente)
        ambiente.relogio.avancar(hours=24)

        with pytest.raises(TokenInvalido):
            _confirmar(ambiente, token)

    def test_token_desconhecido_gera_erro(self, ambiente):
        with pytest.raises(TokenInvalido):
            _confirmar(ambiente, "token-que-nao-existe")

    def test_nao_aplica_a_senha_quando_o_email_ja_estava_verificado(self, ambiente):
        token = _cadastrar(ambiente)
        usuario = ambiente.usuarios.buscar_por_email(Email("ana@exemplo.com"))
        ambiente.usuarios.atualizar(usuario.verificar_email())

        _confirmar(ambiente, token)

        assert ambiente.usuarios.obter_senha_hash(usuario.id) is None

    def test_confirmacao_nao_sobrescreve_senha_de_conta_ja_verificada(self, ambiente):
        token = _cadastrar(ambiente)
        usuario = ambiente.usuarios.buscar_por_email(Email("ana@exemplo.com"))
        ambiente.usuarios.atualizar(usuario.verificar_email())
        ambiente.usuarios.definir_senha_hash(usuario.id, "hash::senha-do-dono-12")

        _confirmar(ambiente, token)

        assert ambiente.usuarios.obter_senha_hash(usuario.id) == "hash::senha-do-dono-12"

    def test_confirmar_descarta_outros_links_pendentes(self, ambiente):
        token = _cadastrar(ambiente)
        usuario = ambiente.usuarios.buscar_por_email(Email("ana@exemplo.com"))
        outra = _cadastrar(ambiente, senha="outra-senha-longa-2")

        _confirmar(ambiente, outra)

        with pytest.raises(TokenInvalido):
            _confirmar(ambiente, token)
        assert ambiente.usuarios.obter_senha_hash(usuario.id) == ambiente.hasher.gerar("outra-senha-longa-2")
