"""Caso de uso: envia o link de redefinição de senha, sem revelar se o e-mail tem cadastro."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Callable

from jobsync.autenticacao.domain.configuracao import ConfiguracaoAutenticacao
from jobsync.autenticacao.domain.email import Email
from jobsync.autenticacao.domain.enviador_email import EnviadorEmail
from jobsync.autenticacao.domain.exceptions import EmailInvalido
from jobsync.autenticacao.domain.token_opaco import gerar_token, hash_token
from jobsync.autenticacao.domain.token_uso_unico import Finalidade, TokenUsoUnico
from jobsync.autenticacao.domain.token_uso_unico_repository import TokenUsoUnicoRepository
from jobsync.autenticacao.domain.usuario_repository import UsuarioRepository
from jobsync.autenticacao.service_layer import mensagens_email
from jobsync.shared_kernel.domain.relogio import agora_utc


@dataclass
class SolicitarRedefinicaoSenha:
    _usuarios: UsuarioRepository
    _tokens: TokenUsoUnicoRepository
    _enviador: EnviadorEmail
    _config: ConfiguracaoAutenticacao
    _relogio: Callable[[], datetime] = agora_utc

    def executar(self, email: str) -> None:
        try:
            email_vo = Email(email)
        except EmailInvalido:
            return
        usuario = self._usuarios.buscar_por_email(email_vo)
        if usuario is None or not usuario.email_verificado:
            return
        self._tokens.remover_do_usuario(usuario.id, Finalidade.REDEFINICAO_SENHA)
        token = gerar_token()
        validade = self._config.validade_redefinicao_senha
        self._tokens.salvar(
            TokenUsoUnico.emitir(
                hash_token(token), usuario.id, Finalidade.REDEFINICAO_SENHA, self._relogio(), validade
            )
        )
        link = self._config.link_do_frontend("/redefinir-senha", token=token)
        assunto, corpo = mensagens_email.redefinicao_de_senha(link, int(validade.total_seconds() // 60))
        self._enviador.enviar(email_vo, assunto, corpo)
