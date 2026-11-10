"""Caso de uso: conclui o login com um provedor e resolve qual usuário entrou.

Ordem de resolução da identidade: (1) identidade já vinculada; (2) recusa se o provedor não
verificou o e-mail; (3) usuário existente com o mesmo e-mail é vinculado; (4) usuário novo.
O vínculo usa (provedor, subject) como chave, nunca o e-mail.
"""
from __future__ import annotations

import hmac
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Mapping, Optional

from jobsync.autenticacao.domain.configuracao import ConfiguracaoAutenticacao
from jobsync.autenticacao.domain.email import Email
from jobsync.autenticacao.domain.estado_oauth_repository import EstadoOAuthRepository
from jobsync.autenticacao.domain.exceptions import (
    EmailInvalido,
    EmailNaoVerificado,
    EstadoOAuthInvalido,
    IdentidadeJaVinculada,
    ProvedorDesconhecido,
    ProvedorIndisponivel,
    UsuarioDuplicado,
)
from jobsync.autenticacao.domain.identidade_externa import IdentidadeExterna
from jobsync.autenticacao.domain.provedor_identidade import IdentidadeAutenticada, ProvedorIdentidade
from jobsync.autenticacao.domain.token_opaco import hash_token
from jobsync.autenticacao.domain.token_uso_unico import Finalidade
from jobsync.autenticacao.domain.token_uso_unico_repository import TokenUsoUnicoRepository
from jobsync.autenticacao.domain.usuario import Usuario, novo_identificador_de_perfil
from jobsync.autenticacao.domain.usuario_repository import UsuarioRepository
from jobsync.autenticacao.service_layer.emitir_sessao.service import EmitirSessao
from jobsync.autenticacao.service_layer.sessao_iniciada import SessaoIniciada
from jobsync.shared_kernel.domain.relogio import agora_utc

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ResultadoLoginOAuth:
    sessao: SessaoIniciada
    destino: str


@dataclass
class ConcluirLoginOAuth:
    _provedores: Mapping[str, ProvedorIdentidade]
    _estados: EstadoOAuthRepository
    _usuarios: UsuarioRepository
    _tokens: TokenUsoUnicoRepository
    _emitir_sessao: EmitirSessao
    _config: ConfiguracaoAutenticacao
    _relogio: Callable[[], datetime] = agora_utc

    def executar(
        self, provedor: str, codigo: str, estado: str, estado_do_cookie: Optional[str]
    ) -> ResultadoLoginOAuth:
        adaptador = self._provedores.get(provedor)
        if adaptador is None:
            raise ProvedorDesconhecido(f"Provedor não configurado: {provedor}")
        if not estado_do_cookie or not hmac.compare_digest(estado, estado_do_cookie):
            logger.warning("oauth_estado_invalido motivo=cookie")
            raise EstadoOAuthInvalido("O estado do login não confere com o navegador.")
        guardado = self._estados.consumir(hash_token(estado), self._relogio())
        if guardado is None or guardado.provedor != provedor:
            logger.warning("oauth_estado_invalido motivo=desconhecido_ou_expirado")
            raise EstadoOAuthInvalido("O estado do login é inválido ou expirou.")

        identidade = adaptador.trocar_codigo(codigo, guardado.code_verifier, guardado.nonce)
        usuario = self._resolver_usuario(identidade)
        token = self._emitir_sessao.executar(usuario.id)
        logger.info("login_sucesso metodo=%s usuario_id=%s", provedor, usuario.id)
        return ResultadoLoginOAuth(SessaoIniciada(token=token, usuario=usuario), guardado.destino)

    def _resolver_usuario(self, identidade: IdentidadeAutenticada) -> Usuario:
        vinculado = self._usuarios.buscar_por_identidade(identidade.provedor, identidade.subject)
        if vinculado is not None:
            return vinculado
        if not identidade.email_verificado:
            logger.warning("oauth_email_nao_verificado provedor=%s", identidade.provedor)
            raise EmailNaoVerificado("O provedor não confirmou o e-mail.")
        try:
            email = Email(identidade.email)
        except EmailInvalido as erro:
            logger.warning("oauth_email_invalido provedor=%s", identidade.provedor)
            raise ProvedorIndisponivel("O provedor devolveu um e-mail inválido.") from erro

        existente = self._usuarios.buscar_por_email(email)
        usuario = self._verificar_existente(existente) if existente else self._criar(email, identidade)
        self._vincular(usuario, identidade)
        return usuario

    def _verificar_existente(self, usuario: Usuario) -> Usuario:
        verificado = usuario if usuario.email_verificado else usuario.verificar_email()
        if verificado is not usuario:
            self._usuarios.atualizar(verificado)
        self._tokens.remover_do_usuario(usuario.id, Finalidade.CONFIRMACAO_EMAIL)
        return verificado

    def _criar(self, email: Email, identidade: IdentidadeAutenticada) -> Usuario:
        novo = Usuario.novo(
            email, novo_identificador_de_perfil(), self._relogio(), nome=identidade.nome
        ).verificar_email()
        try:
            self._usuarios.salvar_novo(novo)
        except UsuarioDuplicado:
            concorrente = self._usuarios.buscar_por_email(email)
            if concorrente is None:
                raise
            return self._verificar_existente(concorrente)
        logger.info("usuario_criado usuario_id=%s metodo=%s", novo.id, identidade.provedor)
        return novo

    def _vincular(self, usuario: Usuario, identidade: IdentidadeAutenticada) -> None:
        try:
            self._usuarios.vincular_identidade(
                IdentidadeExterna(identidade.provedor, identidade.subject, usuario.id)
            )
        except IdentidadeJaVinculada:
            dono = self._usuarios.buscar_por_identidade(identidade.provedor, identidade.subject)
            if dono is None or dono.id != usuario.id:
                raise
            return
        logger.info("vinculo_realizado usuario_id=%s provedor=%s", usuario.id, identidade.provedor)
