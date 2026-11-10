"""Composição dos serviços de autenticação: junta casos de uso, adapters e configuração."""
from __future__ import annotations

import logging
import os
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Callable

from psycopg_pool import ConnectionPool

from jobsync.autenticacao.adapters import (
    EnviadorEmailLog,
    EnviadorEmailSmtp,
    EstadoOAuthRepositoryImpl,
    HasherSenhaArgon2,
    LimiteTentativasRepositoryImpl,
    ProvedorGoogle,
    SessaoRepositoryImpl,
    TokenUsoUnicoRepositoryImpl,
    UsuarioRepositoryImpl,
)
from jobsync.autenticacao.domain.configuracao import ConfiguracaoAutenticacao
from jobsync.autenticacao.domain.enviador_email import EnviadorEmail
from jobsync.autenticacao.domain.estado_oauth_repository import EstadoOAuthRepository
from jobsync.autenticacao.domain.hasher_senha import HasherSenha
from jobsync.autenticacao.domain.limite_tentativas_repository import LimiteTentativasRepository
from jobsync.autenticacao.domain.provedor_identidade import ProvedorIdentidade
from jobsync.autenticacao.domain.sessao_repository import SessaoRepository
from jobsync.autenticacao.domain.token_uso_unico_repository import TokenUsoUnicoRepository
from jobsync.autenticacao.domain.usuario_repository import UsuarioRepository
from jobsync.autenticacao.service_layer.cadastrar_usuario import CadastrarUsuario
from jobsync.autenticacao.service_layer.concluir_login_oauth import ConcluirLoginOAuth
from jobsync.autenticacao.service_layer.confirmar_email import ConfirmarEmail
from jobsync.autenticacao.service_layer.emitir_sessao import EmitirSessao
from jobsync.autenticacao.service_layer.encerrar_sessao import EncerrarSessao
from jobsync.autenticacao.service_layer.entrar_com_identificador_simples import EntrarComIdentificadorSimples
from jobsync.autenticacao.service_layer.entrar_com_senha import EntrarComSenha
from jobsync.autenticacao.service_layer.iniciar_login_oauth import IniciarLoginOAuth
from jobsync.autenticacao.service_layer.redefinir_senha import RedefinirSenha
from jobsync.autenticacao.service_layer.resolver_sessao import ResolverSessao
from jobsync.autenticacao.service_layer.solicitar_redefinicao_senha import SolicitarRedefinicaoSenha
from jobsync.entrypoints.autenticacao_config import (
    ConfiguracaoHttpAutenticacao,
    configuracao_autenticacao_do_ambiente,
    configuracao_http_do_ambiente,
)
from jobsync.shared_kernel.domain.relogio import agora_utc

logger = logging.getLogger(__name__)

_CAMINHO_RETORNO = "/v1/provedores/{provedor}/retorno"


@dataclass(frozen=True)
class ServicosAutenticacao:
    """Tudo o que a camada HTTP precisa para autenticar, num só ponto de injeção."""

    cadastrar_usuario: CadastrarUsuario
    confirmar_email: ConfirmarEmail
    entrar_com_senha: EntrarComSenha
    entrar_com_identificador_simples: EntrarComIdentificadorSimples
    solicitar_redefinicao_senha: SolicitarRedefinicaoSenha
    redefinir_senha: RedefinirSenha
    resolver_sessao: ResolverSessao
    encerrar_sessao: EncerrarSessao
    iniciar_login_oauth: IniciarLoginOAuth
    concluir_login_oauth: ConcluirLoginOAuth
    provedores: Mapping[str, ProvedorIdentidade]
    config: ConfiguracaoAutenticacao
    http: ConfiguracaoHttpAutenticacao


def montar_servicos_autenticacao(
    *,
    usuarios: UsuarioRepository,
    sessoes: SessaoRepository,
    tokens: TokenUsoUnicoRepository,
    estados: EstadoOAuthRepository,
    limites: LimiteTentativasRepository,
    hasher: HasherSenha,
    enviador: EnviadorEmail,
    provedores: Mapping[str, ProvedorIdentidade],
    config: ConfiguracaoAutenticacao,
    http: ConfiguracaoHttpAutenticacao,
    relogio: Callable[[], datetime] = agora_utc,
) -> ServicosAutenticacao:
    emitir_sessao = EmitirSessao(sessoes, config, relogio)
    return ServicosAutenticacao(
        cadastrar_usuario=CadastrarUsuario(usuarios, tokens, hasher, enviador, config, relogio),
        confirmar_email=ConfirmarEmail(usuarios, tokens, relogio),
        entrar_com_senha=EntrarComSenha(usuarios, limites, hasher, emitir_sessao, config, relogio),
        entrar_com_identificador_simples=EntrarComIdentificadorSimples(usuarios, emitir_sessao, relogio),
        solicitar_redefinicao_senha=SolicitarRedefinicaoSenha(usuarios, tokens, enviador, config, relogio),
        redefinir_senha=RedefinirSenha(usuarios, tokens, sessoes, hasher, relogio),
        resolver_sessao=ResolverSessao(usuarios, sessoes, config, relogio),
        encerrar_sessao=EncerrarSessao(sessoes),
        iniciar_login_oauth=IniciarLoginOAuth(provedores, estados, config, relogio),
        concluir_login_oauth=ConcluirLoginOAuth(
            provedores, estados, usuarios, tokens, emitir_sessao, config, relogio
        ),
        provedores=provedores,
        config=config,
        http=http,
    )


def provedores_do_ambiente(ambiente: Mapping[str, str], config: ConfiguracaoAutenticacao) -> dict[str, ProvedorIdentidade]:
    """Só registra o Google quando as credenciais do cliente OAuth estão configuradas."""
    provedores: dict[str, ProvedorIdentidade] = {}
    client_id = ambiente.get("GOOGLE_CLIENT_ID", "").strip()
    client_secret = ambiente.get("GOOGLE_CLIENT_SECRET", "").strip()
    if client_id and client_secret:
        base = (ambiente.get("AUTH_REDIRECT_BASE_URL") or config.url_frontend).rstrip("/")
        provedores["google"] = ProvedorGoogle(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=base + _CAMINHO_RETORNO.format(provedor="google"),
        )
    else:
        logger.warning("Login com Google desabilitado: defina GOOGLE_CLIENT_ID e GOOGLE_CLIENT_SECRET.")
    return provedores


def enviador_email_do_ambiente(ambiente: Mapping[str, str]) -> EnviadorEmail:
    """SMTP quando `SMTP_HOST` existe; senão apenas registra o e-mail em log (desenvolvimento)."""
    host = ambiente.get("SMTP_HOST", "").strip()
    if not host:
        logger.warning("SMTP_HOST ausente: e-mails de autenticação serão apenas registrados em log.")
        return EnviadorEmailLog()
    return EnviadorEmailSmtp(
        host=host,
        porta=int(ambiente.get("SMTP_PORT") or 587),
        remetente=ambiente.get("SMTP_FROM") or "nao-responda@job-sync.local",
        usuario=ambiente.get("SMTP_USER") or None,
        senha=ambiente.get("SMTP_PASSWORD") or None,
        usar_starttls=(ambiente.get("SMTP_STARTTLS", "true").strip().lower() not in {"0", "false", "no", "off"}),
    )


def servicos_autenticacao_do_ambiente(
    pool: ConnectionPool, ambiente: Mapping[str, str] = os.environ
) -> ServicosAutenticacao:
    config = configuracao_autenticacao_do_ambiente(ambiente)
    return montar_servicos_autenticacao(
        usuarios=UsuarioRepositoryImpl(pool),
        sessoes=SessaoRepositoryImpl(pool),
        tokens=TokenUsoUnicoRepositoryImpl(pool),
        estados=EstadoOAuthRepositoryImpl(pool),
        limites=LimiteTentativasRepositoryImpl(pool),
        hasher=HasherSenhaArgon2(),
        enviador=enviador_email_do_ambiente(ambiente),
        provedores=provedores_do_ambiente(ambiente, config),
        config=config,
        http=configuracao_http_do_ambiente(ambiente),
    )
