import pytest

from jobsync.shared_kernel.adapters.persistence.executor_migracoes import executar_migracoes


@pytest.fixture
def diretorio_migracoes(tmp_path):
    (tmp_path / "0001_a.sql").write_text("CREATE TABLE teste_migracao_a (id INTEGER);")
    (tmp_path / "0002_b.sql").write_text("CREATE TABLE teste_migracao_b (id INTEGER);")
    return tmp_path


@pytest.fixture
def conexao(pool_postgres_sessao):
    with pool_postgres_sessao.connection() as conexao:
        yield conexao
        conexao.rollback()


class TestExecutarMigracoes:
    def test_aplica_pendentes_em_ordem_e_registra_versoes(self, conexao, diretorio_migracoes):
        aplicadas = executar_migracoes(conexao, diretorio_migracoes)

        registradas = [l[0] for l in conexao.execute("SELECT versao FROM schema_migrations").fetchall()]
        assert aplicadas == ["0001_a", "0002_b"]
        assert {"0001_a", "0002_b"} <= set(registradas)

    def test_segunda_execucao_nao_reaplica(self, conexao, diretorio_migracoes):
        executar_migracoes(conexao, diretorio_migracoes)

        aplicadas = executar_migracoes(conexao, diretorio_migracoes)

        assert aplicadas == []

    def test_reverter_a_transacao_desfaz_tabelas_e_registro(self, pool_postgres_sessao, diretorio_migracoes):
        with pool_postgres_sessao.connection() as conexao:
            executar_migracoes(conexao, diretorio_migracoes)
            conexao.rollback()

            existe = conexao.execute("SELECT to_regclass('teste_migracao_a')").fetchone()[0]
            versoes = [l[0] for l in conexao.execute("SELECT versao FROM schema_migrations").fetchall()]

        assert existe is None
        assert "0001_a" not in versoes


class TestSchemaInicial:
    def test_cria_as_seis_tabelas_com_os_tipos_esperados(self, pool_postgres):
        with pool_postgres.connection() as conexao:
            tipos = dict(
                conexao.execute(
                    """
                    SELECT table_name || '.' || column_name, data_type
                    FROM information_schema.columns
                    WHERE table_schema = 'public'
                    """
                ).fetchall()
            )

        assert tipos["curriculo_salvo.pdf_bytes"] == "bytea"
        assert tipos["curriculo_salvo.data_upload"] == "timestamp with time zone"
        assert tipos["vaga.convertida_em_candidatura"] == "boolean"
        assert tipos["perfil_estruturado.experiencias_json"] == "jsonb"
        assert tipos["candidatura.data_aplicacao"] == "timestamp with time zone"
        assert tipos["candidatura.posicao"] == "integer"
