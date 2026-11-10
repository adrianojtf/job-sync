import os

import pytest

from jobsync.shared_kernel.adapters.persistence.conexao_postgres import criar_pool
from jobsync.shared_kernel.adapters.persistence.executor_migracoes import executar_migracoes

_TABELAS = (
    "limite_tentativa",
    "estado_oauth",
    "candidatura",
    "perfil_estruturado",
    "token_captura",
    "vaga",
    "curriculo_salvo",
    "perfil",
)


@pytest.fixture(scope="session")
def url_banco_teste():
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip("Defina TEST_DATABASE_URL para rodar os testes que usam PostgreSQL")
    return url


@pytest.fixture(scope="session")
def pool_postgres_sessao(url_banco_teste):
    pool = criar_pool(url_banco_teste, tamanho_maximo=5)
    with pool.connection() as conexao:
        executar_migracoes(conexao)
    yield pool
    pool.close()


@pytest.fixture
def pool_postgres(pool_postgres_sessao):
    with pool_postgres_sessao.connection() as conexao:
        conexao.execute(f"TRUNCATE {', '.join(_TABELAS)} CASCADE")
    return pool_postgres_sessao
