"""Teste de concorrência do LimiteTentativasRepositoryImpl."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

from jobsync.autenticacao.adapters import LimiteTentativasRepositoryImpl
from jobsync.autenticacao.domain.limite_tentativa import PoliticaLimiteTentativas

AGORA = datetime(2026, 1, 10, 12, 0, tzinfo=timezone.utc)
POLITICA = PoliticaLimiteTentativas(max_falhas=100, janela=timedelta(minutes=15), bloqueio=timedelta(minutes=10))


class TestLimiteTentativasRepositoryImpl:
    def test_falhas_concorrentes_nao_perdem_contagem(self, pool_postgres):
        repositorio = LimiteTentativasRepositoryImpl(pool_postgres)

        with ThreadPoolExecutor(max_workers=5) as executor:
            list(executor.map(lambda _: repositorio.registrar_falha("email:abc", AGORA, POLITICA), range(20)))

        assert repositorio.obter("email:abc").contagem == 20
