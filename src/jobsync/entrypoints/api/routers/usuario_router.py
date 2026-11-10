"""Router de usuários: cadastro, confirmação de e-mail, redefinição de senha e usuário atual."""

from __future__ import annotations

from fastapi import APIRouter, Response, status

from jobsync.entrypoints.api.dependencies import ServicosAutenticacaoDep, UsuarioAutenticadoDep
from jobsync.entrypoints.api.schemas.autenticacao import (
    CadastroRequest,
    MensagemResponse,
    NovaSenhaRequest,
    SolicitacaoRedefinicaoRequest,
    UsuarioResponse,
)
from jobsync.entrypoints.api.schemas.erro import ProblemaResponse

router = APIRouter(tags=["usuários"])

_MENSAGEM_CADASTRO = "Se o e-mail puder ser cadastrado, enviamos um link de confirmação."
_MENSAGEM_REDEFINICAO = "Se o e-mail tiver cadastro, enviamos um link para redefinir a senha."


@router.post(
    "/usuarios",
    response_model=MensagemResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Cadastrar com e-mail e senha",
    description=(
        "Envia um link de confirmação. A senha só passa a valer depois da confirmação. "
        "A resposta é a mesma para e-mails novos e já cadastrados."
    ),
    responses={
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ProblemaResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ProblemaResponse},
    },
)
def cadastrar(body: CadastroRequest, servicos: ServicosAutenticacaoDep) -> MensagemResponse:
    servicos.cadastrar_usuario.executar(body.email, body.senha)
    return MensagemResponse(mensagem=_MENSAGEM_CADASTRO)


@router.get(
    "/usuarios/me",
    response_model=UsuarioResponse,
    status_code=status.HTTP_200_OK,
    summary="Usuário da sessão atual",
    responses={status.HTTP_401_UNAUTHORIZED: {"model": ProblemaResponse}},
)
def obter_usuario_atual(usuario: UsuarioAutenticadoDep) -> UsuarioResponse:
    return UsuarioResponse.from_domain(usuario)


@router.put(
    "/confirmacoes-email/{token}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Confirmar e-mail",
    description="Confirma o e-mail pelo link recebido e ativa a senha escolhida no cadastro.",
    responses={status.HTTP_400_BAD_REQUEST: {"model": ProblemaResponse}},
)
def confirmar_email(token: str, servicos: ServicosAutenticacaoDep) -> Response:
    servicos.confirmar_email.executar(token)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/redefinicoes-senha",
    response_model=MensagemResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Pedir redefinição de senha",
    description="Envia o link se o e-mail tiver cadastro confirmado. A resposta é sempre a mesma.",
    responses={status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ProblemaResponse}},
)
def solicitar_redefinicao(body: SolicitacaoRedefinicaoRequest, servicos: ServicosAutenticacaoDep) -> MensagemResponse:
    servicos.solicitar_redefinicao_senha.executar(body.email)
    return MensagemResponse(mensagem=_MENSAGEM_REDEFINICAO)


@router.put(
    "/redefinicoes-senha/{token}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Definir nova senha",
    description="Troca a senha pelo link recebido e encerra todas as sessões do usuário.",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ProblemaResponse},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ProblemaResponse},
    },
)
def redefinir_senha(token: str, body: NovaSenhaRequest, servicos: ServicosAutenticacaoDep) -> Response:
    servicos.redefinir_senha.executar(token, body.nova_senha)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
