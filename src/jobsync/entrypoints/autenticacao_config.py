"""Leitura da configuração de autenticação a partir das variáveis de ambiente (AUTH_*)."""
from __future__ import annotations

import os
from collections.abc import Mapping
from functools import lru_cache
from dataclasses import dataclass
from datetime import timedelta
from urllib.parse import urlparse

from jobsync.autenticacao.domain.configuracao import ConfiguracaoAutenticacao

_VERDADEIROS = {"1", "true", "yes", "on"}
_PADRAO = ConfiguracaoAutenticacao()


@dataclass(frozen=True)
class ConfiguracaoHttpAutenticacao:
    """Opções da camada HTTP: cookies, origens aceitas em escritas e o login legado."""

    cookie_secure: bool = False
    login_simples_habilitado: bool = False
    origens_permitidas: tuple[str, ...] = ()
    nome_cookie_sessao: str = "js_sessao"
    nome_cookie_oauth: str = "js_oauth"
    # Cabeçalho em que o proxy de confiança informa o IP real (ex.: X-Forwarded-For). Sem ele,
    # vale o endereço da conexão; cabeçalhos enviados pelo cliente nunca são considerados.
    cabecalho_ip_cliente: str | None = None


def _verdadeiro(valor: str | None) -> bool:
    return (valor or "").strip().lower() in _VERDADEIROS


def _dias(valor: str | None, padrao: timedelta) -> timedelta:
    try:
        dias = int((valor or "").strip())
    except ValueError:
        return padrao
    return timedelta(days=dias) if dias > 0 else padrao


def _origem(url: str) -> str:
    partes = urlparse(url)
    return f"{partes.scheme}://{partes.netloc}"


def configuracao_autenticacao_do_ambiente(ambiente: Mapping[str, str]) -> ConfiguracaoAutenticacao:
    maxima = _dias(ambiente.get("AUTH_SESSAO_MAXIMA_DIAS"), _PADRAO.sessao_maxima)
    inatividade = _dias(ambiente.get("AUTH_SESSAO_INATIVIDADE_DIAS"), _PADRAO.sessao_inatividade)
    return ConfiguracaoAutenticacao(
        url_frontend=ambiente.get("AUTH_BASE_URL_FRONTEND") or _PADRAO.url_frontend,
        sessao_maxima=maxima,
        sessao_inatividade=min(inatividade, maxima),
    )


def configuracao_http_do_ambiente(ambiente: Mapping[str, str]) -> ConfiguracaoHttpAutenticacao:
    frontend = ambiente.get("AUTH_BASE_URL_FRONTEND") or _PADRAO.url_frontend
    cors = [o.strip() for o in (ambiente.get("CORS_ORIGINS") or "").split(",") if o.strip() and o.strip() != "*"]
    origens = tuple(dict.fromkeys([_origem(frontend), *cors]))
    return ConfiguracaoHttpAutenticacao(
        cookie_secure=_verdadeiro(ambiente.get("AUTH_COOKIE_SECURE")),
        login_simples_habilitado=_verdadeiro(ambiente.get("AUTH_LOGIN_SIMPLES_HABILITADO")),
        origens_permitidas=origens,
        cabecalho_ip_cliente=(ambiente.get("AUTH_CABECALHO_IP_CLIENTE") or "").strip() or None,
    )


@lru_cache(maxsize=1)
def obter_configuracao_http() -> ConfiguracaoHttpAutenticacao:
    """Configuração HTTP do processo, lida do ambiente na primeira necessidade."""
    return configuracao_http_do_ambiente(os.environ)
