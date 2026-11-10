import pytest

from jobsync.entrypoints.cli.migrar_sqlite_para_postgres import (
    ERRO_DESTINO,
    ERRO_ORIGEM,
    SUCESSO,
    principal,
)
from jobsync.tests.shared_kernel.banco_sqlite_antigo import criar_sqlite


@pytest.fixture
def ambiente(url_banco_teste, pool_postgres, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", url_banco_teste)


@pytest.fixture
def sqlite_origem(tmp_path):
    caminho = tmp_path / "job_sync.db"
    criar_sqlite(caminho)
    return caminho


class TestPrincipal:
    def test_sucesso_imprime_relatorio_e_devolve_zero(self, ambiente, sqlite_origem, capsys):
        codigo = principal(["--sqlite", str(sqlite_origem), "--fuso-origem", "America/Sao_Paulo"])

        saida = capsys.readouterr().out
        assert codigo == SUCESSO
        assert "MIGRAÇÃO CONCLUÍDA" in saida
        assert "candidatura" in saida
        assert "PDFs conferidos por hash: 2" in saida

    def test_avisos_de_curriculo_removido_aparecem_no_relatorio(self, ambiente, tmp_path, capsys):
        caminho = tmp_path / "orfao.db"
        criar_sqlite(
            caminho,
            extra="""
            INSERT INTO candidatura VALUES
              ('c4', 'ana', NULL, 'removido-1', 'Delta', 'Dev', 'APLICADO',
               '2026-03-15T10:00:00', '2026-03-15T10:00:00', 2);
            """,
        )

        codigo = principal(["--sqlite", str(caminho), "--fuso-origem", "UTC"])

        saida = capsys.readouterr().out
        assert codigo == SUCESSO
        assert "Avisos:" in saida
        assert "removido-1" in saida

    def test_dry_run_informa_simulacao(self, ambiente, sqlite_origem, capsys):
        codigo = principal(["--sqlite", str(sqlite_origem), "--dry-run", "--fuso-origem", "UTC"])

        assert codigo == SUCESSO
        assert "SIMULAÇÃO (nada foi gravado)" in capsys.readouterr().out

    def test_origem_com_problemas_devolve_codigo_2(self, ambiente, tmp_path, capsys):
        codigo = principal(["--sqlite", str(tmp_path / "nao-existe.db")])

        assert codigo == ERRO_ORIGEM
        assert "não encontrado" in capsys.readouterr().err

    def test_fuso_desconhecido_devolve_codigo_2(self, ambiente, sqlite_origem, capsys):
        codigo = principal(["--sqlite", str(sqlite_origem), "--fuso-origem", "Marte/Olympus"])

        assert codigo == ERRO_ORIGEM
        assert "Fuso desconhecido" in capsys.readouterr().err

    def test_destino_com_dados_devolve_codigo_3(self, ambiente, sqlite_origem, capsys):
        principal(["--sqlite", str(sqlite_origem), "--fuso-origem", "UTC"])
        capsys.readouterr()

        codigo = principal(["--sqlite", str(sqlite_origem), "--fuso-origem", "UTC"])

        assert codigo == ERRO_DESTINO
        assert "já tem dados" in capsys.readouterr().err

    def test_sem_database_url_devolve_codigo_3_sem_vazar_credenciais(
        self, sqlite_origem, monkeypatch, capsys
    ):
        monkeypatch.delenv("DATABASE_URL", raising=False)
        monkeypatch.setattr("jobsync.entrypoints.cli.migrar_sqlite_para_postgres.load_dotenv", lambda: None)

        codigo = principal(["--sqlite", str(sqlite_origem)])

        assert codigo == ERRO_DESTINO
        assert "DATABASE_URL" in capsys.readouterr().err

    def test_nunca_imprime_a_senha_do_destino(self, sqlite_origem, monkeypatch, capsys):
        monkeypatch.setenv("DATABASE_URL", "postgresql://usuario:segredo123@127.0.0.1:1/job_sync")
        monkeypatch.setattr("jobsync.entrypoints.cli.migrar_sqlite_para_postgres.load_dotenv", lambda: None)

        principal(["--sqlite", str(sqlite_origem), "--fuso-origem", "UTC"])

        capturado = capsys.readouterr()
        assert "segredo123" not in capturado.out + capturado.err
