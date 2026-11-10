"""Testes dos adapters de envio de e-mail."""

import logging
import smtplib

import pytest

from jobsync.autenticacao.adapters.enviador_email_log import EnviadorEmailLog
from jobsync.autenticacao.adapters.enviador_email_smtp import EnviadorEmailSmtp
from jobsync.autenticacao.domain.email import Email
from jobsync.autenticacao.domain.exceptions import EnvioEmailFalhou


class SmtpFalso:
    instancias: list["SmtpFalso"] = []

    def __init__(self, host, port, timeout=None):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.starttls_chamado = False
        self.login_chamado = None
        self.mensagens = []
        SmtpFalso.instancias.append(self)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def starttls(self):
        self.starttls_chamado = True

    def login(self, usuario, senha):
        self.login_chamado = (usuario, senha)

    def send_message(self, mensagem):
        self.mensagens.append(mensagem)


class SmtpQuebrado(SmtpFalso):
    def send_message(self, mensagem):
        raise smtplib.SMTPException("falha")


@pytest.fixture(autouse=True)
def _limpar_instancias():
    SmtpFalso.instancias.clear()


def _enviador(fabrica=SmtpFalso, **extras):
    return EnviadorEmailSmtp(
        host="smtp.exemplo.com",
        porta=587,
        remetente="nao-responda@exemplo.com",
        fabrica_smtp=fabrica,
        **extras,
    )


class TestEnviadorEmailSmtp:
    def test_envia_mensagem_com_remetente_destinatario_assunto_e_corpo(self):
        _enviador().enviar(Email("ana@exemplo.com"), "Confirme seu e-mail", "Clique no link")

        mensagem = SmtpFalso.instancias[0].mensagens[0]
        assert mensagem["To"] == "ana@exemplo.com"
        assert mensagem["From"] == "nao-responda@exemplo.com"
        assert mensagem["Subject"] == "Confirme seu e-mail"
        assert "Clique no link" in mensagem.get_content()

    def test_usa_starttls_por_padrao(self):
        _enviador().enviar(Email("ana@exemplo.com"), "Assunto", "Corpo")

        assert SmtpFalso.instancias[0].starttls_chamado is True

    def test_nao_usa_starttls_quando_desabilitado(self):
        _enviador(usar_starttls=False).enviar(Email("ana@exemplo.com"), "Assunto", "Corpo")

        assert SmtpFalso.instancias[0].starttls_chamado is False

    def test_autentica_quando_ha_credenciais(self):
        _enviador(usuario="u", senha="s").enviar(Email("ana@exemplo.com"), "Assunto", "Corpo")

        assert SmtpFalso.instancias[0].login_chamado == ("u", "s")

    def test_nao_autentica_sem_credenciais(self):
        _enviador().enviar(Email("ana@exemplo.com"), "Assunto", "Corpo")

        assert SmtpFalso.instancias[0].login_chamado is None

    def test_falha_do_smtp_vira_envio_email_falhou(self):
        with pytest.raises(EnvioEmailFalhou):
            _enviador(SmtpQuebrado).enviar(Email("ana@exemplo.com"), "Assunto", "Corpo")

    def test_falha_de_conexao_vira_envio_email_falhou(self):
        def fabrica(host, port, timeout=None):
            raise OSError("sem rede")

        with pytest.raises(EnvioEmailFalhou):
            _enviador(fabrica).enviar(Email("ana@exemplo.com"), "Assunto", "Corpo")


class TestEnviadorEmailLog:
    def test_registra_o_corpo_para_uso_em_desenvolvimento(self, caplog):
        with caplog.at_level(logging.INFO):
            EnviadorEmailLog().enviar(Email("ana@exemplo.com"), "Confirme", "http://localhost/confirmar?token=abc")

        assert "http://localhost/confirmar?token=abc" in caplog.text

    def test_nao_registra_o_endereco_completo(self, caplog):
        with caplog.at_level(logging.INFO):
            EnviadorEmailLog().enviar(Email("ana@exemplo.com"), "Confirme", "corpo")

        assert "ana@exemplo.com" not in caplog.text
        assert "@exemplo.com" in caplog.text
