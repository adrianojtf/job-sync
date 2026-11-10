import os

import pytest

from jobsync.entrypoints.dependencies import fechar_pool_conexoes


@pytest.fixture(autouse=True)
def banco_de_teste_da_api(monkeypatch):
    url = os.getenv("TEST_DATABASE_URL")
    if url:
        monkeypatch.setenv("DATABASE_URL", url)
    yield
    fechar_pool_conexoes()
