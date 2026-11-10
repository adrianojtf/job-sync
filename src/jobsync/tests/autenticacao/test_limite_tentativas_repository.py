"""Testes de contrato do LimiteTentativasRepository (fake e PostgreSQL)."""

from datetime import datetime, timedelta, timezone

from jobsync.autenticacao.domain.limite_tentativa import PoliticaLimiteTentativas

AGORA = datetime(2026, 1, 10, 12, 0, tzinfo=timezone.utc)
POLITICA = PoliticaLimiteTentativas(max_falhas=3, janela=timedelta(minutes=15), bloqueio=timedelta(minutes=10))


class TestLimiteTentativasRepository:
    def test_chave_sem_falhas_devolve_none(self, repositorios):
        assert repositorios.limites.obter("email:abc") is None

    def test_registrar_falha_acumula_a_contagem(self, repositorios):
        repositorios.limites.registrar_falha("email:abc", AGORA, POLITICA)

        limite = repositorios.limites.registrar_falha("email:abc", AGORA, POLITICA)

        assert limite.contagem == 2
        assert repositorios.limites.obter("email:abc") == limite

    def test_bloqueia_ao_atingir_o_maximo(self, repositorios):
        for _ in range(3):
            limite = repositorios.limites.registrar_falha("email:abc", AGORA, POLITICA)

        assert limite.bloqueado(AGORA) is True
        assert repositorios.limites.obter("email:abc").bloqueado(AGORA) is True

    def test_chaves_diferentes_sao_independentes(self, repositorios):
        for _ in range(3):
            repositorios.limites.registrar_falha("email:abc", AGORA, POLITICA)

        outro = repositorios.limites.registrar_falha("ip:1.2.3.4", AGORA, POLITICA)

        assert outro.contagem == 1
        assert outro.bloqueado(AGORA) is False

    def test_limpar_remove_o_registro(self, repositorios):
        repositorios.limites.registrar_falha("email:abc", AGORA, POLITICA)

        repositorios.limites.limpar("email:abc")

        assert repositorios.limites.obter("email:abc") is None
