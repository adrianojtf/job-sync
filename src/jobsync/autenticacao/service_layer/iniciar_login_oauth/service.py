"""Caso de uso: começa o login com um provedor (Authorization Code + PKCE)."""
from __future__ import annotations

import base64
import hashlib
import secrets
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Mapping, Optional

from jobsync.autenticacao.domain.configuracao import ConfiguracaoAutenticacao
from jobsync.autenticacao.domain.destino import destino_seguro
from jobsync.autenticacao.domain.estado_oauth import EstadoOAuth
from jobsync.autenticacao.domain.estado_oauth_repository import EstadoOAuthRepository
from jobsync.autenticacao.domain.exceptions import ProvedorDesconhecido
from jobsync.autenticacao.domain.provedor_identidade import ProvedorIdentidade
from jobsync.autenticacao.domain.token_opaco import gerar_token, hash_token
from jobsync.shared_kernel.domain.relogio import agora_utc

_BYTES_DO_VERIFICADOR = 48


@dataclass(frozen=True)
class InicioLoginOAuth:
    """URL para onde redirecionar e o valor do `state`, que também vai no cookie do navegador."""

    url: str
    estado: str


def calcular_code_challenge(code_verifier: str) -> str:
    digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


@dataclass
class IniciarLoginOAuth:
    _provedores: Mapping[str, ProvedorIdentidade]
    _estados: EstadoOAuthRepository
    _config: ConfiguracaoAutenticacao
    _relogio: Callable[[], datetime] = agora_utc

    def executar(self, provedor: str, destino: Optional[str]) -> InicioLoginOAuth:
        adaptador = self._provedores.get(provedor)
        if adaptador is None:
            raise ProvedorDesconhecido(f"Provedor não configurado: {provedor}")
        estado = gerar_token()
        nonce = gerar_token()
        code_verifier = secrets.token_urlsafe(_BYTES_DO_VERIFICADOR)
        self._estados.salvar(
            EstadoOAuth.iniciar(
                hash_token(estado),
                provedor,
                code_verifier,
                nonce,
                destino_seguro(destino),
                self._relogio(),
                self._config.validade_estado_oauth,
            )
        )
        url = adaptador.url_autorizacao(estado, nonce, calcular_code_challenge(code_verifier))
        return InicioLoginOAuth(url=url, estado=estado)
