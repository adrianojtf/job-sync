"""Caso de uso: confirma o e-mail por link de uso único e ativa a senha escolhida no cadastro."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Callable

from jobsync.autenticacao.domain.exceptions import TokenInvalido
from jobsync.autenticacao.domain.token_opaco import hash_token
from jobsync.autenticacao.domain.token_uso_unico import Finalidade
from jobsync.autenticacao.domain.token_uso_unico_repository import TokenUsoUnicoRepository
from jobsync.autenticacao.domain.usuario_repository import UsuarioRepository
from jobsync.shared_kernel.domain.relogio import agora_utc

logger = logging.getLogger(__name__)


@dataclass
class ConfirmarEmail:
    _usuarios: UsuarioRepository
    _tokens: TokenUsoUnicoRepository
    _relogio: Callable[[], datetime] = agora_utc

    def executar(self, token: str) -> None:
        consumido = self._tokens.consumir(hash_token(token), Finalidade.CONFIRMACAO_EMAIL, self._relogio())
        if consumido is None:
            logger.warning("token_uso_unico_invalido finalidade=%s", Finalidade.CONFIRMACAO_EMAIL.value)
            raise TokenInvalido("Link inválido ou expirado.")
        usuario = self._usuarios.buscar_por_id(consumido.usuario_id)
        if usuario is None:
            raise TokenInvalido("Link inválido ou expirado.")
        if not usuario.email_verificado:
            self._usuarios.atualizar(usuario.verificar_email())
            if consumido.carga:
                self._usuarios.definir_senha_hash(usuario.id, consumido.carga)
            logger.info("email_confirmado usuario_id=%s", usuario.id)
        self._tokens.remover_do_usuario(usuario.id, Finalidade.CONFIRMACAO_EMAIL)
