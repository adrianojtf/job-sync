"""Proteção contra CSRF: em escritas com cookie de sessão, a origem precisa ser conhecida.

Complementa o `SameSite=Lax` do cookie. Sem cookie de sessão não há credencial ambiente a
proteger, então clientes que não são navegadores (extensão, scripts) passam sem `Origin`.
Referência: OWASP Cross-Site Request Forgery Prevention Cheat Sheet.
"""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Optional
from urllib.parse import urlparse

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from jobsync.entrypoints.autenticacao_config import ConfiguracaoHttpAutenticacao

_METODOS_DE_ESCRITA = {"POST", "PUT", "PATCH", "DELETE"}


def _origem_da_requisicao(request: Request) -> Optional[str]:
    origem = request.headers.get("origin")
    if origem:
        return origem
    referer = request.headers.get("referer")
    if not referer:
        return None
    partes = urlparse(referer)
    return f"{partes.scheme}://{partes.netloc}"


def _permitida(origem: str, request: Request, config: ConfiguracaoHttpAutenticacao) -> bool:
    if origem in config.origens_permitidas:
        return True
    return urlparse(origem).netloc == request.headers.get("host")


def adicionar_protecao_csrf(app: FastAPI, obter_config: Callable[[], ConfiguracaoHttpAutenticacao]) -> None:
    @app.middleware("http")
    async def _verificar_origem(request: Request, call_next: Callable[[Request], Awaitable]):
        config = obter_config()
        if request.method in _METODOS_DE_ESCRITA and config.nome_cookie_sessao in request.cookies:
            origem = _origem_da_requisicao(request)
            if origem is not None and not _permitida(origem, request, config):
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={
                        "type": "https://jobsync.com/erros/origem-nao-permitida",
                        "title": "Origem não permitida",
                        "status": status.HTTP_403_FORBIDDEN,
                        "detail": "A origem da requisição não é permitida.",
                        "instance": str(request.url),
                    },
                )
        return await call_next(request)
