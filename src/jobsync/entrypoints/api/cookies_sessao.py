"""Cookies da autenticação: sessão (`js_sessao`) e estado temporário do login OAuth (`js_oauth`)."""
from __future__ import annotations

from fastapi import Response

from jobsync.entrypoints.autenticacao_config import ConfiguracaoHttpAutenticacao

CAMINHO_COOKIE_OAUTH = "/v1/provedores"
VALIDADE_COOKIE_OAUTH_SEGUNDOS = 600


def definir_cookie_sessao(
    resposta: Response, token: str, http: ConfiguracaoHttpAutenticacao, validade_segundos: int
) -> None:
    resposta.set_cookie(
        key=http.nome_cookie_sessao,
        value=token,
        max_age=validade_segundos,
        path="/",
        httponly=True,
        samesite="lax",
        secure=http.cookie_secure,
    )


def remover_cookie_sessao(resposta: Response, http: ConfiguracaoHttpAutenticacao) -> None:
    resposta.delete_cookie(
        key=http.nome_cookie_sessao, path="/", httponly=True, samesite="lax", secure=http.cookie_secure
    )


def definir_cookie_oauth(resposta: Response, estado: str, http: ConfiguracaoHttpAutenticacao) -> None:
    resposta.set_cookie(
        key=http.nome_cookie_oauth,
        value=estado,
        max_age=VALIDADE_COOKIE_OAUTH_SEGUNDOS,
        path=CAMINHO_COOKIE_OAUTH,
        httponly=True,
        samesite="lax",
        secure=http.cookie_secure,
    )


def remover_cookie_oauth(resposta: Response, http: ConfiguracaoHttpAutenticacao) -> None:
    resposta.delete_cookie(
        key=http.nome_cookie_oauth,
        path=CAMINHO_COOKIE_OAUTH,
        httponly=True,
        samesite="lax",
        secure=http.cookie_secure,
    )
