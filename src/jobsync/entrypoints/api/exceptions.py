"""Exception handlers centralizados no formato RFC 7807 (Problem Details)."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse

from jobsync.autenticacao.domain.exceptions import (
    AcessoNegado,
    CredenciaisInvalidas,
    EmailInvalido,
    EnvioEmailFalhou,
    LimiteTentativasExcedido,
    NaoAutenticado,
    ProvedorDesconhecido,
    ProvedorIndisponivel,
    SenhaInvalida,
    TokenInvalido,
)
from jobsync.curriculo_salvo.domain.limite_curriculos_salvos import LimiteCurriculosSalvosExcedido
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
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        headers=headers,
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

    @app.exception_handler(LimiteCurriculosSalvosExcedido)
    async def _limite_curriculos_salvos_excedido_handler(
        request: Request, exc: LimiteCurriculosSalvosExcedido
    ) -> JSONResponse:
        return _problem_response(
            request=request,
            status_code=status.HTTP_409_CONFLICT,
            title="Biblioteca de currículos cheia",
            detail=(
                "Sua biblioteca de currículos está cheia. "
                "Remova um currículo para confirmar a candidatura."
            ),
            type_slug="limite-curriculos-salvos",
        )

    def _registrar_autenticacao(
        excecao: type[Exception],
        status_code: int,
        title: str,
        type_slug: str,
        detail: str | None = None,
    ) -> None:
        @app.exception_handler(excecao)
        async def _handler(request: Request, exc: Exception) -> JSONResponse:
            return _problem_response(
                request=request,
                status_code=status_code,
                title=title,
                detail=detail or str(exc),
                type_slug=type_slug,
            )

    _registrar_autenticacao(NaoAutenticado, status.HTTP_401_UNAUTHORIZED, "Não autenticado", "nao-autenticado", "Faça login para continuar.")
    _registrar_autenticacao(AcessoNegado, status.HTTP_403_FORBIDDEN, "Acesso negado", "acesso-negado", "Você não tem acesso a este recurso.")
    _registrar_autenticacao(CredenciaisInvalidas, status.HTTP_401_UNAUTHORIZED, "Credenciais inválidas", "credenciais-invalidas", "E-mail ou senha incorretos.")
    _registrar_autenticacao(TokenInvalido, status.HTTP_400_BAD_REQUEST, "Link inválido", "token-invalido", "Link inválido ou expirado.")
    _registrar_autenticacao(EmailInvalido, status.HTTP_422_UNPROCESSABLE_ENTITY, "Requisição inválida", "requisicao-invalida")
    _registrar_autenticacao(SenhaInvalida, status.HTTP_422_UNPROCESSABLE_ENTITY, "Requisição inválida", "requisicao-invalida")
    _registrar_autenticacao(EnvioEmailFalhou, status.HTTP_503_SERVICE_UNAVAILABLE, "E-mail indisponível", "email-indisponivel", "Não foi possível enviar o e-mail agora. Tente novamente em instantes.")
    _registrar_autenticacao(ProvedorDesconhecido, status.HTTP_404_NOT_FOUND, "Provedor desconhecido", "provedor-desconhecido", "Provedor de login não encontrado.")
    _registrar_autenticacao(ProvedorIndisponivel, status.HTTP_502_BAD_GATEWAY, "Provedor indisponível", "provedor-indisponivel", "Não foi possível autenticar com o provedor.")

    @app.exception_handler(LimiteTentativasExcedido)
    async def _limite_tentativas_handler(request: Request, exc: LimiteTentativasExcedido) -> JSONResponse:
        return _problem_response(
            request=request,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            title="Muitas tentativas",
            detail="Muitas tentativas. Tente novamente mais tarde.",
            type_slug="limite-tentativas",
            headers={"Retry-After": str(exc.retry_after_segundos)},
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
