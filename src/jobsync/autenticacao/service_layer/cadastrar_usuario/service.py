"""Caso de uso: cadastro com e-mail e senha.

A senha escolhida só passa a valer quando o e-mail é confirmado: o hash viaja na carga do
token de confirmação. Assim, quem cadastra o e-mail de outra pessoa não consegue deixar uma
senha ativa na conta dela.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Callable

from jobsync.autenticacao.domain.configuracao import ConfiguracaoAutenticacao
from jobsync.autenticacao.domain.email import Email
from jobsync.autenticacao.domain.enviador_email import EnviadorEmail
from jobsync.autenticacao.domain.exceptions import UsuarioDuplicado
from jobsync.autenticacao.domain.hasher_senha import HasherSenha
from jobsync.autenticacao.domain.senha import Senha
from jobsync.autenticacao.domain.token_opaco import gerar_token, hash_token
from jobsync.autenticacao.domain.token_uso_unico import Finalidade, TokenUsoUnico
from jobsync.autenticacao.domain.token_uso_unico_repository import TokenUsoUnicoRepository
from jobsync.autenticacao.domain.usuario import Usuario, novo_identificador_de_perfil
from jobsync.autenticacao.domain.usuario_repository import UsuarioRepository
from jobsync.autenticacao.service_layer import mensagens_email
from jobsync.shared_kernel.domain.relogio import agora_utc

logger = logging.getLogger(__name__)


@dataclass
class CadastrarUsuario:
    _usuarios: UsuarioRepository
    _tokens: TokenUsoUnicoRepository
    _hasher: HasherSenha
    _enviador: EnviadorEmail
    _config: ConfiguracaoAutenticacao
    _relogio: Callable[[], datetime] = agora_utc

    def executar(self, email: str, senha: str) -> None:
        """Não revela se o e-mail já tinha cadastro: o resultado é o mesmo nos dois casos."""
        email_vo = Email(email)
        senha_vo = Senha(senha, email=email_vo)
        usuario = self._usuario_para(email_vo)
        if usuario.email_verificado:
            self._avisar_conta_existente(email_vo)
            return
        self._enviar_confirmacao(usuario, email_vo, self._hasher.gerar(senha_vo.valor))

    def _usuario_para(self, email: Email) -> Usuario:
        existente = self._usuarios.buscar_por_email(email)
        if existente is not None:
            return existente
        novo = Usuario.novo(email, novo_identificador_de_perfil(), self._relogio())
        try:
            self._usuarios.salvar_novo(novo)
        except UsuarioDuplicado:
            concorrente = self._usuarios.buscar_por_email(email)
            if concorrente is None:
                raise
            return concorrente
        logger.info("usuario_criado usuario_id=%s metodo=senha", novo.id)
        return novo

    def _enviar_confirmacao(self, usuario: Usuario, email: Email, senha_hash: str) -> None:
        self._tokens.remover_do_usuario(usuario.id, Finalidade.CONFIRMACAO_EMAIL)
        token = gerar_token()
        validade = self._config.validade_confirmacao_email
        self._tokens.salvar(
            TokenUsoUnico.emitir(
                hash_token(token),
                usuario.id,
                Finalidade.CONFIRMACAO_EMAIL,
                self._relogio(),
                validade,
                carga=senha_hash,
            )
        )
        link = self._config.link_do_frontend("/confirmar-email", token=token)
        assunto, corpo = mensagens_email.confirmacao_de_cadastro(link, int(validade.total_seconds() // 3600))
        self._enviador.enviar(email, assunto, corpo)

    def _avisar_conta_existente(self, email: Email) -> None:
        assunto, corpo = mensagens_email.conta_ja_existente(
            self._config.link_do_frontend("/entrar"),
            self._config.link_do_frontend("/recuperar-senha"),
        )
        self._enviador.enviar(email, assunto, corpo)
