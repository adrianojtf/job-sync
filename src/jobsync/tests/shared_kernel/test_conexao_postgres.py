import pytest

from jobsync.shared_kernel.adapters.persistence.conexao_postgres import (
    ErroConexaoBanco,
    criar_pool,
    descrever_destino,
    obter_url_banco,
)


class TestObterUrlBanco:
    def test_devolve_a_url_da_variavel_de_ambiente(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "postgresql://u:s@localhost:5432/job_sync")

        url = obter_url_banco()

        assert url == "postgresql://u:s@localhost:5432/job_sync"

    def test_sem_variavel_levanta_erro_com_exemplo(self, monkeypatch):
        monkeypatch.delenv("DATABASE_URL", raising=False)

        with pytest.raises(ErroConexaoBanco, match="DATABASE_URL"):
            obter_url_banco()


class TestDescreverDestino:
    def test_omite_usuario_e_senha(self):
        descricao = descrever_destino("postgresql://adriano:segredo@db.local:5433/job_sync")

        assert descricao == "db.local:5433/job_sync"
        assert "segredo" not in descricao
        assert "adriano" not in descricao


class TestCriarPool:
    def test_banco_inacessivel_levanta_erro_sem_expor_a_senha(self, monkeypatch):
        monkeypatch.setattr(
            "jobsync.shared_kernel.adapters.persistence.conexao_postgres._TIMEOUT_CONEXAO_SEGUNDOS", 1.0
        )

        with pytest.raises(ErroConexaoBanco) as erro:
            criar_pool("postgresql://usuario:segredo@127.0.0.1:1/job_sync")

        assert "segredo" not in str(erro.value)
        assert "127.0.0.1:1/job_sync" in str(erro.value)
