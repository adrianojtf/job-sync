"""Testes de contrato do EstadoOAuthRepository (fake e PostgreSQL)."""

from datetime import datetime, timedelta, timezone

from jobsync.autenticacao.domain.estado_oauth import EstadoOAuth

AGORA = datetime(2026, 1, 10, 12, 0, tzinfo=timezone.utc)


def _estado() -> EstadoOAuth:
    return EstadoOAuth.iniciar(b"estado-1", "google", "verificador", "nonce", "/vagas", AGORA, timedelta(minutes=10))


class TestEstadoOAuthRepository:
    def test_consumir_devolve_o_estado_salvo(self, repositorios):
        estado = _estado()
        repositorios.estados.salvar(estado)

        assert repositorios.estados.consumir(b"estado-1", AGORA) == estado

    def test_estado_so_pode_ser_consumido_uma_vez(self, repositorios):
        repositorios.estados.salvar(_estado())
        repositorios.estados.consumir(b"estado-1", AGORA)

        assert repositorios.estados.consumir(b"estado-1", AGORA) is None

    def test_estado_expirado_devolve_none_e_e_descartado(self, repositorios):
        repositorios.estados.salvar(_estado())
        depois = AGORA + timedelta(minutes=10)

        assert repositorios.estados.consumir(b"estado-1", depois) is None
        assert repositorios.estados.consumir(b"estado-1", AGORA) is None

    def test_estado_inexistente_devolve_none(self, repositorios):
        assert repositorios.estados.consumir(b"nada", AGORA) is None
