"""Testes do serviço IniciarLoginOAuth."""

import base64
import hashlib
from datetime import timedelta

import pytest

from jobsync.autenticacao.domain.exceptions import ProvedorDesconhecido
from jobsync.autenticacao.domain.token_opaco import hash_token
from jobsync.autenticacao.service_layer.iniciar_login_oauth.service import IniciarLoginOAuth
from jobsync.tests.autenticacao.dobles import ProvedorFalso


@pytest.fixture
def provedor():
    return ProvedorFalso()


@pytest.fixture
def servico(ambiente, provedor):
    return IniciarLoginOAuth({"google": provedor}, ambiente.estados, ambiente.config, ambiente.relogio)


class TestIniciarLoginOAuth:
    def test_devolve_a_url_do_provedor_e_o_valor_do_cookie(self, servico, provedor):
        inicio = servico.executar("google", "/vagas")

        assert inicio.url.startswith("https://idp.teste/auth?")
        assert inicio.estado == provedor.ultima_url_autorizacao["estado"]

    def test_guarda_somente_o_hash_do_estado(self, ambiente, servico):
        inicio = servico.executar("google", "/vagas")

        guardado = ambiente.estados.consumir(hash_token(inicio.estado), ambiente.relogio.agora)
        assert guardado.provedor == "google"
        assert guardado.estado_hash != inicio.estado.encode()

    def test_code_challenge_e_o_sha256_do_verificador_em_base64_url(self, ambiente, servico, provedor):
        inicio = servico.executar("google", "/")

        guardado = ambiente.estados.consumir(hash_token(inicio.estado), ambiente.relogio.agora)
        esperado = base64.urlsafe_b64encode(hashlib.sha256(guardado.code_verifier.encode()).digest()).rstrip(b"=")
        assert provedor.ultima_url_autorizacao["code_challenge"] == esperado.decode()
        assert 43 <= len(guardado.code_verifier) <= 128

    def test_nonce_guardado_e_o_enviado_ao_provedor(self, ambiente, servico, provedor):
        inicio = servico.executar("google", "/")

        guardado = ambiente.estados.consumir(hash_token(inicio.estado), ambiente.relogio.agora)
        assert guardado.nonce == provedor.ultima_url_autorizacao["nonce"]

    def test_estado_vale_por_10_minutos(self, ambiente, servico):
        inicio = servico.executar("google", "/")

        guardado = ambiente.estados.consumir(hash_token(inicio.estado), ambiente.relogio.agora)
        assert guardado.expira_em == ambiente.relogio.agora + timedelta(minutes=10)

    def test_destino_valido_e_guardado(self, ambiente, servico):
        inicio = servico.executar("google", "/candidaturas")

        guardado = ambiente.estados.consumir(hash_token(inicio.estado), ambiente.relogio.agora)
        assert guardado.destino == "/candidaturas"

    @pytest.mark.parametrize("destino", [None, "//evil.com", "https://evil.com"])
    def test_destino_perigoso_vira_raiz(self, ambiente, servico, destino):
        inicio = servico.executar("google", destino)

        guardado = ambiente.estados.consumir(hash_token(inicio.estado), ambiente.relogio.agora)
        assert guardado.destino == "/"

    def test_cada_inicio_gera_estado_e_nonce_diferentes(self, servico, provedor):
        primeiro = servico.executar("google", "/")
        nonce_primeiro = provedor.ultima_url_autorizacao["nonce"]

        segundo = servico.executar("google", "/")

        assert primeiro.estado != segundo.estado
        assert nonce_primeiro != provedor.ultima_url_autorizacao["nonce"]

    def test_provedor_desconhecido_gera_erro(self, servico):
        with pytest.raises(ProvedorDesconhecido):
            servico.executar("facebook", "/")
