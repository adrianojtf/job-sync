"""Router de sessões: login com e-mail e senha, login legado (dev) e logout."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, Response, status

from jobsync.entrypoints.api.cookies_sessao import definir_cookie_sessao, remover_cookie_sessao
from jobsync.entrypoints.api.dependencies import ServicosAutenticacaoDep
from jobsync.entrypoints.api.schemas.autenticacao import (
    LoginRequest,
    LoginSimplesRequest,
    UsuarioResponse,
)
from jobsync.entrypoints.api.schemas.erro import ProblemaResponse

router = APIRouter(tags=["sessões"])

_LOCATION_SESSAO_ATUAL = "/v1/sessoes/atual"


def _ip_do_cliente(request: Request, cabecalho: str | None) -> str | None:
    """IP real do cliente. Atrás de um proxy, todo mundo chega com o IP dele; por isso, com o
    cabeçalho configurado, vale a última entrada, que é a que o próprio proxy acrescentou."""
    if cabecalho:
        valor = request.headers.get(cabecalho, "")
        ultimo = valor.split(",")[-1].strip()
        if ultimo:
            return ultimo
    return request.client.host if request.client else None


@router.post(
    "/sessoes",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Entrar com e-mail e senha",
    description="Cria a sessão e a entrega em cookie HttpOnly. O erro não diz se o e-mail existe.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ProblemaResponse},
        status.HTTP_429_TOO_MANY_REQUESTS: {"model": ProblemaResponse},
    },
)
def entrar(
    body: LoginRequest,
    request: Request,
    response: Response,
    servicos: ServicosAutenticacaoDep,
) -> UsuarioResponse:
    sessao = servicos.entrar_com_senha.executar(body.email, body.senha, ip=_ip_do_cliente(request, servicos.http.cabecalho_ip_cliente))
    definir_cookie_sessao(
        response, sessao.token, servicos.http, int(servicos.config.sessao_maxima.total_seconds())
    )
    response.headers["Location"] = _LOCATION_SESSAO_ATUAL
    return UsuarioResponse.from_domain(sessao.usuario)


@router.post(
    "/sessoes/simples",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Entrar por identificador (somente desenvolvimento)",
    description="Existe só com AUTH_LOGIN_SIMPLES_HABILITADO=true; caso contrário responde 404.",
    responses={status.HTTP_404_NOT_FOUND: {"model": ProblemaResponse}},
)
def entrar_com_identificador(
    body: LoginSimplesRequest,
    response: Response,
    servicos: ServicosAutenticacaoDep,
) -> UsuarioResponse:
    if not servicos.http.login_simples_habilitado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recurso não encontrado.")
    sessao = servicos.entrar_com_identificador_simples.executar(body.identificador)
    definir_cookie_sessao(
        response, sessao.token, servicos.http, int(servicos.config.sessao_maxima.total_seconds())
    )
    response.headers["Location"] = _LOCATION_SESSAO_ATUAL
    return UsuarioResponse.from_domain(sessao.usuario)


@router.delete(
    "/sessoes/atual",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Sair",
    description="Encerra a sessão atual e limpa o cookie. Sem sessão, também responde 204.",
)
def sair(request: Request, servicos: ServicosAutenticacaoDep) -> Response:
    servicos.encerrar_sessao.executar(request.cookies.get(servicos.http.nome_cookie_sessao))
    resposta = Response(status_code=status.HTTP_204_NO_CONTENT)
    remover_cookie_sessao(resposta, servicos.http)
    return resposta
