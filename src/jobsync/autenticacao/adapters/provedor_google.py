"""Adapter de ProvedorIdentidade para o Google (OpenID Connect, Authorization Code + PKCE).

Referência: https://developers.google.com/identity/openid-connect/openid-connect
"""
from __future__ import annotations

import hmac
import logging
from typing import Any, Callable, Optional
from urllib.parse import urlencode

import httpx
import jwt

from jobsync.autenticacao.domain.exceptions import ProvedorIndisponivel
from jobsync.autenticacao.domain.provedor_identidade import IdentidadeAutenticada

logger = logging.getLogger(__name__)

URL_AUTORIZACAO = "https://accounts.google.com/o/oauth2/v2/auth"
URL_TOKEN = "https://oauth2.googleapis.com/token"
URL_CHAVES_PUBLICAS = "https://www.googleapis.com/oauth2/v3/certs"
EMISSORES = ("https://accounts.google.com", "accounts.google.com")
ESCOPOS = "openid email profile"
_TIMEOUT_SEGUNDOS = 10
_TOLERANCIA_RELOGIO_SEGUNDOS = 10
_CLAIMS_OBRIGATORIAS = ["exp", "iat", "iss", "aud", "sub", "email", "nonce"]


def _resolvedor_padrao() -> Callable[[str], Any]:
    cliente_jwks = jwt.PyJWKClient(URL_CHAVES_PUBLICAS, cache_keys=True)
    return lambda token: cliente_jwks.get_signing_key_from_jwt(token).key


def _como_booleano(valor: Any) -> bool:
    if isinstance(valor, bool):
        return valor
    return isinstance(valor, str) and valor.lower() == "true"


class ProvedorGoogle:
    nome = "google"

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        cliente_http: Optional[httpx.Client] = None,
        resolvedor_chave: Optional[Callable[[str], Any]] = None,
    ) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self._redirect_uri = redirect_uri
        self._http = cliente_http or httpx.Client(timeout=_TIMEOUT_SEGUNDOS)
        self._resolver_chave = resolvedor_chave or _resolvedor_padrao()

    def url_autorizacao(self, estado: str, nonce: str, code_challenge: str) -> str:
        parametros = {
            "client_id": self._client_id,
            "redirect_uri": self._redirect_uri,
            "response_type": "code",
            "scope": ESCOPOS,
            "state": estado,
            "nonce": nonce,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }
        return f"{URL_AUTORIZACAO}?{urlencode(parametros)}"

    def trocar_codigo(self, codigo: str, code_verifier: str, nonce: str) -> IdentidadeAutenticada:
        id_token = self._obter_id_token(codigo, code_verifier)
        claims = self._validar_id_token(id_token, nonce)
        return IdentidadeAutenticada(
            provedor=self.nome,
            subject=str(claims["sub"]),
            email=str(claims["email"]),
            email_verificado=_como_booleano(claims.get("email_verified")),
            nome=claims.get("name"),
        )

    def _obter_id_token(self, codigo: str, code_verifier: str) -> str:
        try:
            resposta = self._http.post(
                URL_TOKEN,
                data={
                    "code": codigo,
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                    "redirect_uri": self._redirect_uri,
                    "grant_type": "authorization_code",
                    "code_verifier": code_verifier,
                },
            )
        except httpx.HTTPError as erro:
            raise self._falha("rede", erro) from erro
        if resposta.status_code != 200:
            raise self._falha(f"status_{resposta.status_code}")
        try:
            id_token = resposta.json().get("id_token")
        except (ValueError, AttributeError) as erro:
            raise self._falha("resposta_invalida", erro) from erro
        if not isinstance(id_token, str) or not id_token:
            raise self._falha("sem_id_token")
        return id_token

    def _validar_id_token(self, id_token: str, nonce: str) -> dict[str, Any]:
        try:
            chave = self._resolver_chave(id_token)
            claims = jwt.decode(
                id_token,
                chave,
                algorithms=["RS256"],
                audience=self._client_id,
                issuer=list(EMISSORES),
                leeway=_TOLERANCIA_RELOGIO_SEGUNDOS,
                options={"require": _CLAIMS_OBRIGATORIAS},
            )
        except (jwt.PyJWTError, httpx.HTTPError, OSError) as erro:
            raise self._falha(type(erro).__name__, erro) from erro
        if not hmac.compare_digest(str(claims["nonce"]), nonce):
            raise self._falha("nonce_invalido")
        return claims

    def _falha(self, motivo: str, causa: Optional[BaseException] = None) -> ProvedorIndisponivel:
        logger.warning("Falha no provedor %s: %s", self.nome, motivo)
        return ProvedorIndisponivel("Não foi possível autenticar com o provedor.")
