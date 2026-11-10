"""Testes da entidade EstadoOAuth."""

from datetime import datetime, timedelta, timezone

import pytest

from jobsync.autenticacao.domain.estado_oauth import EstadoOAuth

AGORA = datetime(2026, 1, 10, 12, 0, tzinfo=timezone.utc)


def _estado(validade: timedelta = timedelta(minutes=10)) -> EstadoOAuth:
    return EstadoOAuth.iniciar(b"hash", "google", "verificador", "nonce", "/vagas", AGORA, validade)


class TestEstadoOAuth:
    def test_iniciar_define_validade(self):
        estado = _estado()

        assert estado.expira_em == AGORA + timedelta(minutes=10)
        assert estado.provedor == "google"
        assert estado.destino == "/vagas"

    def test_nao_expirado_dentro_da_validade(self):
        assert _estado().expirado(AGORA + timedelta(minutes=9)) is False

    def test_expirado_apos_a_validade(self):
        assert _estado().expirado(AGORA + timedelta(minutes=10)) is True

    @pytest.mark.parametrize("campo", ["provedor", "code_verifier", "nonce", "destino"])
    def test_campo_vazio_gera_erro(self, campo):
        valores = {"provedor": "google", "code_verifier": "v", "nonce": "n", "destino": "/"}
        valores[campo] = ""

        with pytest.raises(ValueError):
            EstadoOAuth.iniciar(
                b"hash",
                valores["provedor"],
                valores["code_verifier"],
                valores["nonce"],
                valores["destino"],
                AGORA,
                timedelta(minutes=10),
            )

    def test_hash_vazio_gera_erro(self):
        with pytest.raises(ValueError):
            EstadoOAuth.iniciar(b"", "google", "v", "n", "/", AGORA, timedelta(minutes=10))
