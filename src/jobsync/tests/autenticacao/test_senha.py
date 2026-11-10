"""Testes do value object Senha e da política de senha."""

import pytest

from jobsync.autenticacao.domain.email import Email
from jobsync.autenticacao.domain.exceptions import SenhaInvalida
from jobsync.autenticacao.domain.senha import Senha


class TestSenha:
    def test_aceita_senha_valida(self):
        senha = Senha("uma-senha-longa-e-boa")

        assert senha.valor == "uma-senha-longa-e-boa"

    def test_nao_expoe_o_valor_na_representacao(self):
        senha = Senha("uma-senha-longa-e-boa")

        assert "uma-senha-longa-e-boa" not in repr(senha)

    def test_rejeita_senha_com_menos_de_10_caracteres(self):
        with pytest.raises(SenhaInvalida):
            Senha("curta123")

    def test_aceita_senha_com_exatamente_10_caracteres(self):
        assert Senha("x7Q!m2Z#p9").valor == "x7Q!m2Z#p9"

    def test_aceita_senha_com_exatamente_128_caracteres(self):
        assert len(Senha("a1" * 64).valor) == 128

    def test_rejeita_senha_com_mais_de_128_caracteres(self):
        with pytest.raises(SenhaInvalida):
            Senha("a" * 129)

    @pytest.mark.parametrize("comum", ["1234567890", "Password123", "QWERTYUIOP", "senha12345"])
    def test_rejeita_senhas_comuns_sem_diferenciar_caixa(self, comum):
        with pytest.raises(SenhaInvalida):
            Senha(comum)

    def test_rejeita_senha_igual_a_parte_local_do_email(self):
        email = Email("mariasilva01@exemplo.com")

        with pytest.raises(SenhaInvalida):
            Senha("MariaSilva01", email=email)

    def test_aceita_senha_igual_a_parte_local_quando_nao_ha_email(self):
        assert Senha("MariaSilva01").valor == "MariaSilva01"

    def test_senha_invalida_e_value_error(self):
        with pytest.raises(ValueError):
            Senha("curta")
