"""Garante que os serviços de autenticação não registram segredos nem e-mails completos."""

import logging

import pytest

from jobsync.autenticacao.domain.exceptions import CredenciaisInvalidas
from jobsync.autenticacao.service_layer.cadastrar_usuario.service import CadastrarUsuario
from jobsync.autenticacao.service_layer.confirmar_email.service import ConfirmarEmail
from jobsync.autenticacao.service_layer.emitir_sessao.service import EmitirSessao
from jobsync.autenticacao.service_layer.entrar_com_senha.service import EntrarComSenha

EMAIL = "ana.secreta@exemplo.com"
SENHA = "senha-super-secreta-1"


class TestLogsSeguros:
    def test_fluxo_de_cadastro_e_login_nao_vaza_dados_sensiveis(self, ambiente, caplog):
        cadastrar = CadastrarUsuario(
            ambiente.usuarios, ambiente.tokens, ambiente.hasher, ambiente.enviador, ambiente.config, ambiente.relogio
        )
        entrar = EntrarComSenha(
            ambiente.usuarios,
            ambiente.limites,
            ambiente.hasher,
            EmitirSessao(ambiente.sessoes, ambiente.config, ambiente.relogio),
            ambiente.config,
            ambiente.relogio,
        )

        with caplog.at_level(logging.DEBUG):
            cadastrar.executar(EMAIL, SENHA)
            token_confirmacao = ambiente.enviador.ultimo_token(EMAIL)
            ConfirmarEmail(ambiente.usuarios, ambiente.tokens, ambiente.relogio).executar(token_confirmacao)
            with pytest.raises(CredenciaisInvalidas):
                entrar.executar(EMAIL, "senha-errada-123", ip="203.0.113.7")
            sessao = entrar.executar(EMAIL, SENHA, ip="203.0.113.7")

        registro = caplog.text
        assert registro
        for sensivel in (EMAIL, SENHA, "senha-errada-123", token_confirmacao, sessao.token, "203.0.113.7"):
            assert sensivel not in registro
