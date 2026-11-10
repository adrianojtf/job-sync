"""Testes do ProvedorGoogle com rede simulada."""

import time
from urllib.parse import parse_qs, urlparse

import httpx
import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from jobsync.autenticacao.adapters.provedor_google import ProvedorGoogle
from jobsync.autenticacao.domain.exceptions import ProvedorIndisponivel

CLIENT_ID = "cliente.apps.googleusercontent.com"
REDIRECT = "http://localhost:8080/v1/provedores/google/retorno"
NONCE = "nonce-esperado"


@pytest.fixture(scope="module")
def chave_privada():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture(scope="module")
def outra_chave_privada():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


def _claims(**sobrescritas):
    agora = int(time.time())
    base = {
        "iss": "https://accounts.google.com",
        "aud": CLIENT_ID,
        "sub": "1234567890",
        "email": "Ana@Exemplo.com",
        "email_verified": True,
        "name": "Ana Souza",
        "nonce": NONCE,
        "iat": agora,
        "exp": agora + 3600,
    }
    base.update(sobrescritas)
    return {k: v for k, v in base.items() if v is not None}


def _id_token(chave, **sobrescritas):
    return jwt.encode(_claims(**sobrescritas), chave, algorithm="RS256")


def _provedor(chave_privada, handler):
    cliente = httpx.Client(transport=httpx.MockTransport(handler))
    return ProvedorGoogle(
        client_id=CLIENT_ID,
        client_secret="segredo",
        redirect_uri=REDIRECT,
        cliente_http=cliente,
        resolvedor_chave=lambda _token: chave_privada.public_key(),
    )


def _resposta_com(id_token):
    return lambda request: httpx.Response(200, json={"id_token": id_token, "access_token": "x"})


class TestUrlAutorizacao:
    def test_monta_url_com_pkce_state_e_nonce(self, chave_privada):
        provedor = _provedor(chave_privada, _resposta_com("x"))

        url = provedor.url_autorizacao(estado="st", nonce="nn", code_challenge="cc")

        partes = urlparse(url)
        consulta = {k: v[0] for k, v in parse_qs(partes.query).items()}
        assert f"{partes.scheme}://{partes.netloc}{partes.path}" == "https://accounts.google.com/o/oauth2/v2/auth"
        assert consulta["client_id"] == CLIENT_ID
        assert consulta["redirect_uri"] == REDIRECT
        assert consulta["response_type"] == "code"
        assert consulta["scope"] == "openid email profile"
        assert consulta["state"] == "st"
        assert consulta["nonce"] == "nn"
        assert consulta["code_challenge"] == "cc"
        assert consulta["code_challenge_method"] == "S256"

    def test_expoe_o_nome_do_provedor(self, chave_privada):
        assert _provedor(chave_privada, _resposta_com("x")).nome == "google"


class TestTrocarCodigo:
    def test_devolve_a_identidade_autenticada(self, chave_privada):
        provedor = _provedor(chave_privada, _resposta_com(_id_token(chave_privada)))

        identidade = provedor.trocar_codigo("codigo", "verificador", NONCE)

        assert identidade.provedor == "google"
        assert identidade.subject == "1234567890"
        assert identidade.email == "Ana@Exemplo.com"
        assert identidade.email_verificado is True
        assert identidade.nome == "Ana Souza"

    def test_envia_codigo_verificador_e_credenciais_ao_endpoint_de_token(self, chave_privada):
        capturadas = []

        def handler(request):
            capturadas.append(request)
            return httpx.Response(200, json={"id_token": _id_token(chave_privada)})

        _provedor(chave_privada, handler).trocar_codigo("codigo-1", "verificador-1", NONCE)

        requisicao = capturadas[0]
        corpo = {k: v[0] for k, v in parse_qs(requisicao.content.decode()).items()}
        assert str(requisicao.url) == "https://oauth2.googleapis.com/token"
        assert corpo["code"] == "codigo-1"
        assert corpo["code_verifier"] == "verificador-1"
        assert corpo["client_id"] == CLIENT_ID
        assert corpo["client_secret"] == "segredo"
        assert corpo["redirect_uri"] == REDIRECT
        assert corpo["grant_type"] == "authorization_code"

    def test_email_verificado_falso_chega_como_falso(self, chave_privada):
        provedor = _provedor(chave_privada, _resposta_com(_id_token(chave_privada, email_verified=False)))

        assert provedor.trocar_codigo("c", "v", NONCE).email_verificado is False

    def test_email_verificado_como_texto_true_e_aceito(self, chave_privada):
        provedor = _provedor(chave_privada, _resposta_com(_id_token(chave_privada, email_verified="true")))

        assert provedor.trocar_codigo("c", "v", NONCE).email_verificado is True

    def test_email_verificado_ausente_vira_falso(self, chave_privada):
        provedor = _provedor(chave_privada, _resposta_com(_id_token(chave_privada, email_verified=None)))

        assert provedor.trocar_codigo("c", "v", NONCE).email_verificado is False

    def test_aceita_issuer_sem_esquema(self, chave_privada):
        provedor = _provedor(chave_privada, _resposta_com(_id_token(chave_privada, iss="accounts.google.com")))

        assert provedor.trocar_codigo("c", "v", NONCE).subject == "1234567890"

    @pytest.mark.parametrize(
        "alteracao",
        [
            {"aud": "outro-cliente"},
            {"iss": "https://evil.example.com"},
            {"exp": int(time.time()) - 3600},
            {"nonce": "outro-nonce"},
            {"nonce": None},
            {"sub": None},
            {"email": None},
        ],
    )
    def test_id_token_invalido_gera_provedor_indisponivel(self, chave_privada, alteracao):
        provedor = _provedor(chave_privada, _resposta_com(_id_token(chave_privada, **alteracao)))

        with pytest.raises(ProvedorIndisponivel):
            provedor.trocar_codigo("c", "v", NONCE)

    def test_assinatura_de_outra_chave_e_recusada(self, chave_privada, outra_chave_privada):
        provedor = _provedor(chave_privada, _resposta_com(_id_token(outra_chave_privada)))

        with pytest.raises(ProvedorIndisponivel):
            provedor.trocar_codigo("c", "v", NONCE)

    def test_token_sem_assinatura_e_recusado(self, chave_privada):
        sem_assinatura = jwt.encode(_claims(), key=None, algorithm="none")
        provedor = _provedor(chave_privada, _resposta_com(sem_assinatura))

        with pytest.raises(ProvedorIndisponivel):
            provedor.trocar_codigo("c", "v", NONCE)

    def test_resposta_de_erro_do_google_gera_provedor_indisponivel(self, chave_privada):
        provedor = _provedor(chave_privada, lambda r: httpx.Response(400, json={"error": "invalid_grant"}))

        with pytest.raises(ProvedorIndisponivel):
            provedor.trocar_codigo("c", "v", NONCE)

    def test_resposta_sem_id_token_gera_provedor_indisponivel(self, chave_privada):
        provedor = _provedor(chave_privada, lambda r: httpx.Response(200, json={"access_token": "x"}))

        with pytest.raises(ProvedorIndisponivel):
            provedor.trocar_codigo("c", "v", NONCE)

    def test_resposta_que_nao_e_json_gera_provedor_indisponivel(self, chave_privada):
        provedor = _provedor(chave_privada, lambda r: httpx.Response(200, text="<html>"))

        with pytest.raises(ProvedorIndisponivel):
            provedor.trocar_codigo("c", "v", NONCE)

    def test_falha_de_rede_gera_provedor_indisponivel(self, chave_privada):
        def handler(request):
            raise httpx.ConnectError("sem rede")

        with pytest.raises(ProvedorIndisponivel):
            _provedor(chave_privada, handler).trocar_codigo("c", "v", NONCE)

    def test_falha_ao_obter_chave_publica_gera_provedor_indisponivel(self, chave_privada):
        def resolvedor(_token):
            raise jwt.PyJWKClientError("jwks fora do ar")

        cliente = httpx.Client(transport=httpx.MockTransport(_resposta_com(_id_token(chave_privada))))
        provedor = ProvedorGoogle(CLIENT_ID, "segredo", REDIRECT, cliente, resolvedor)

        with pytest.raises(ProvedorIndisponivel):
            provedor.trocar_codigo("c", "v", NONCE)

    def test_erro_nao_expoe_o_token(self, chave_privada):
        token = _id_token(chave_privada, aud="outro")
        provedor = _provedor(chave_privada, _resposta_com(token))

        with pytest.raises(ProvedorIndisponivel) as erro:
            provedor.trocar_codigo("c", "v", NONCE)

        assert token not in str(erro.value)
