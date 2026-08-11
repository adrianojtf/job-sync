"""Exception handlers centralizados no formato RFC 7807 (Problem Details)."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


def _problem_response(
    request: Request,
    status_code: int,
    title: str,
    detail: str,
    type_slug: str,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "type": f"https://jobsync.com/erros/{type_slug}",
            "title": title,
            "status": status_code,
            "detail": detail,
            "instance": str(request.url),
        },
    )


def adicionar_handlers_excecao(app: FastAPI) -> None:
    """Registra handlers globais de exceção no app FastAPI."""

    @app.exception_handler(HTTPException)
    async def _http_exception_handler(
        request: Request, exc: HTTPException
    ) -> JSONResponse:
        slug = str(exc.status_code)
        return _problem_response(
            request=request,
            status_code=exc.status_code,
            title=exc.detail or "Erro na requisição",
            detail=exc.detail or "Erro na requisição",
            type_slug=slug,
        )

    @app.exception_handler(RequestValidationError)
    async def _validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        erros = exc.errors()
        detail = "; ".join(
            f"{'.'.join(str(loc) for loc in e.get('loc', []))}: {e.get('msg', '')}"
            for e in erros
        )
        return _problem_response(
            request=request,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            title="Requisição inválida",
            detail=detail,
            type_slug="requisicao-invalida",
        )

    @app.exception_handler(Exception)
    async def _generic_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception("Erro inesperado na API: %s", exc)
        return _problem_response(
            request=request,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            title="Erro interno do servidor",
            detail="Ocorreu um erro inesperado. Tente novamente mais tarde.",
            type_slug="internal-server-error",
        )
