"""Testes da CLI associar_email_perfil."""

import pytest

from jobsync.autenticacao.domain.email import Email
from jobsync.entrypoints.cli.associar_email_perfil import (
    CONFLITO,
    DADOS_INVALIDOS,
    DESTINO_INVALIDO,
    SUCESSO,
    principal,
)
from jobsync.perfil.adapters import PerfilRepositoryImpl
from jobsync.autenticacao.adapters import UsuarioRepositoryImpl


@pytest.fixture
def banco(url_banco_teste, pool_postgres, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", url_banco_teste)
    PerfilRepositoryImpl(pool_postgres).criar("matheus")
    return pool_postgres


class TestPrincipal:
    def test_associa_o_email_ao_perfil_existente(self, banco, capsys):
        codigo = principal(["--perfil", "matheus", "--email", "Matheus@Exemplo.com"])

        usuario = UsuarioRepositoryImpl(banco).buscar_por_email(Email("matheus@exemplo.com"))
        assert codigo == SUCESSO
        assert usuario.perfil_identificador == "matheus"
        assert usuario.email_verificado is False
        assert "associado" in capsys.readouterr().out.lower()

    def test_repetir_e_sucesso_e_informa_que_ja_estava_associado(self, banco, capsys):
        principal(["--perfil", "matheus", "--email", "matheus@exemplo.com"])
        capsys.readouterr()

        codigo = principal(["--perfil", "matheus", "--email", "matheus@exemplo.com"])

        assert codigo == SUCESSO
        assert "já estava" in capsys.readouterr().out

    def test_perfil_inexistente_devolve_dados_invalidos(self, banco, capsys):
        codigo = principal(["--perfil", "ninguem", "--email", "a@b.com"])

        assert codigo == DADOS_INVALIDOS
        assert "ninguem" in capsys.readouterr().err

    def test_email_invalido_devolve_dados_invalidos(self, banco):
        assert principal(["--perfil", "matheus", "--email", "invalido"]) == DADOS_INVALIDOS

    def test_conflito_devolve_codigo_proprio(self, banco, capsys):
        principal(["--perfil", "matheus", "--email", "matheus@exemplo.com"])

        codigo = principal(["--perfil", "matheus", "--email", "outro@exemplo.com"])

        assert codigo == CONFLITO
        assert capsys.readouterr().err

    def test_banco_inacessivel_devolve_destino_invalido(self, monkeypatch, capsys):
        monkeypatch.delenv("DATABASE_URL", raising=False)

        codigo = principal(["--perfil", "matheus", "--email", "a@b.com"])

        assert codigo == DESTINO_INVALIDO
        assert "DATABASE_URL" in capsys.readouterr().err
