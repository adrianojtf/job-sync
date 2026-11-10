"""Testes do value object Email."""

import pytest

from jobsync.autenticacao.domain.email import Email
from jobsync.autenticacao.domain.exceptions import EmailInvalido


class TestEmail:
    def test_normaliza_para_minusculas_e_remove_espacos(self):
        email = Email("  Adriano.Teixeira@Gmail.COM ")

        assert email.valor == "adriano.teixeira@gmail.com"

    def test_expoe_parte_local(self):
        email = Email("maria.silva@exemplo.com")

        assert email.parte_local == "maria.silva"

    def test_emails_com_caixa_diferente_sao_iguais(self):
        assert Email("A@b.com") == Email("a@B.com")

    @pytest.mark.parametrize(
        "valor",
        ["", "   ", "semarroba", "@semlocal.com", "sem@dominio", "dois@@arrobas.com", "com espaco@x.com"],
    )
    def test_formato_invalido_gera_erro(self, valor):
        with pytest.raises(EmailInvalido):
            Email(valor)

    def test_email_acima_de_254_caracteres_gera_erro(self):
        with pytest.raises(EmailInvalido):
            Email("a" * 250 + "@x.com")

    def test_email_invalido_e_value_error(self):
        with pytest.raises(ValueError):
            Email("invalido")

    def test_email_e_imutavel(self):
        email = Email("a@b.com")

        with pytest.raises(Exception):
            email.valor = "outro@b.com"
