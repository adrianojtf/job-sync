"""Router de provedores de identidade: opções de login e fluxo OAuth (Authorization Code + PKCE)."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Request, status
from fastapi.responses import RedirectResponse

from jobsync.autenticacao.domain.exceptions import (
    EmailNaoVerificado,
    EstadoOAuthInvalido,
    ProvedorDesconhecido,
    ProvedorIndisponivel,
)
from jobsync.entrypoints.api.cookies_sessao import (
    definir_cookie_oauth,
    definir_cookie_sessao,
    remover_cookie_oauth,
)
from jobsync.entrypoints.api.dependencies import ServicosAutenticacaoDep
from jobsync.entrypoints.api.schemas.autenticacao import ProvedoresResponse
from jobsync.entrypoints.api.schemas.erro import ProblemaResponse

router = APIRouter(tags=["provedores"])

_CODIGOS_DE_ERRO = {
    EstadoOAuthInvalido: "estado_invalido",
    EmailNaoVerificado: "email_nao_verificado",
    ProvedorIndisponivel: "provedor_indisponivel",
}


@router.get(
    "/provedores",
    response_model=ProvedoresResponse,
    status_code=status.HTTP_200_OK,
    summary="Métodos de entrada disponíveis",
)
def listar_provedores(servicos: ServicosAutenticacaoDep) -> ProvedoresResponse:
    return ProvedoresResponse(
        provedores=sorted(servicos.provedores),
        senha=True,
        login_simples=servicos.http.login_simples_habilitado,
    )


@router.get(
    "/provedores/{provedor}/autorizacao",
    status_code=status.HTTP_302_FOUND,
    summary="Iniciar login com o provedor",
    description="Redireciona para o provedor e grava o estado do login em cookie curto e HttpOnly.",
    responses={status.HTTP_404_NOT_FOUND: {"model": ProblemaResponse}},
)
def iniciar_login(provedor: str, servicos: ServicosAutenticacaoDep, destino: Optional[str] = None) -> RedirectResponse:
    inicio = servicos.iniciar_login_oauth.executar(provedor, destino)
    resposta = RedirectResponse(inicio.url, status_code=status.HTTP_302_FOUND)
    definir_cookie_oauth(resposta, inicio.estado, servicos.http)
    return resposta


@router.get(
    "/provedores/{provedor}/retorno",
    status_code=status.HTTP_302_FOUND,
    summary="Retorno do provedor",
    description=(
        "Conclui o login e redireciona ao frontend. Falhas voltam para /entrar?erro=<codigo> "
        "com códigos fixos: acesso_negado, estado_invalido, email_nao_verificado, provedor_indisponivel."
    ),
    responses={status.HTTP_404_NOT_FOUND: {"model": ProblemaResponse}},
)
def concluir_login(
    provedor: str,
    request: Request,
    servicos: ServicosAutenticacaoDep,
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
) -> RedirectResponse:
    if provedor not in servicos.provedores:
        raise ProvedorDesconhecido(f"Provedor não configurado: {provedor}")
    http = servicos.http

    def voltar_com_erro(codigo: str) -> RedirectResponse:
        resposta = RedirectResponse(
            servicos.config.link_do_frontend("/entrar", erro=codigo), status_code=status.HTTP_302_FOUND
        )
        remover_cookie_oauth(resposta, http)
        return resposta

    if error:
        return voltar_com_erro("acesso_negado")
    if not code or not state:
        return voltar_com_erro("estado_invalido")
    try:
        resultado = servicos.concluir_login_oauth.executar(
            provedor, code, state, request.cookies.get(http.nome_cookie_oauth)
        )
    except tuple(_CODIGOS_DE_ERRO) as erro:
        return voltar_com_erro(_CODIGOS_DE_ERRO[type(erro)])

    resposta = RedirectResponse(
        servicos.config.link_do_frontend(resultado.destino), status_code=status.HTTP_302_FOUND
    )
    definir_cookie_sessao(
        resposta, resultado.sessao.token, http, int(servicos.config.sessao_maxima.total_seconds())
    )
    remover_cookie_oauth(resposta, http)
    return resposta
