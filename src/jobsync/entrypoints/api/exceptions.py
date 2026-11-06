"""Exception handlers centralizados no formato RFC 7807 (Problem Details)."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse

from jobsync.vaga.service_layer.avaliar_descricao_vaga.exceptions import (
    AvaliacaoDescricaoVagaIndisponivel,
)
from jobsync.curriculo.service_layer.avaliar_experiencia.exceptions import (
    AvaliacaoExperienciaIndisponivel,
)
from jobsync.curriculo.service_layer.sugestao_ia_indisponivel import SugestaoIAIndisponivel

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

    @app.exception_handler(AvaliacaoDescricaoVagaIndisponivel)
    async def _avaliacao_descricao_vaga_indisponivel_handler(
        request: Request, exc: AvaliacaoDescricaoVagaIndisponivel
    ) -> JSONResponse:
        return _problem_response(
            request=request,
            status_code=status.HTTP_502_BAD_GATEWAY,
            title="Avaliação de vaga indisponível",
            detail=str(exc),
            type_slug="avaliacao-vaga-indisponivel",
        )

    @app.exception_handler(AvaliacaoExperienciaIndisponivel)
    async def _avaliacao_experiencia_indisponivel_handler(
        request: Request, exc: AvaliacaoExperienciaIndisponivel
    ) -> JSONResponse:
        return _problem_response(
            request=request,
            status_code=status.HTTP_502_BAD_GATEWAY,
            title="Avaliação de experiência indisponível",
            detail=str(exc),
            type_slug="avaliacao-experiencia-indisponivel",
        )

    @app.exception_handler(SugestaoIAIndisponivel)
    async def _sugestao_ia_indisponivel_handler(
        request: Request, exc: SugestaoIAIndisponivel
    ) -> JSONResponse:
        return _problem_response(
            request=request,
            status_code=status.HTTP_502_BAD_GATEWAY,
            title="Sugestão de IA indisponível",
            detail=str(exc),
            type_slug="sugestao-ia-indisponivel",
        )

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
