"""Caso de uso: define uma nova senha a partir do link de redefinição."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Callable

from jobsync.autenticacao.domain.exceptions import TokenInvalido
from jobsync.autenticacao.domain.hasher_senha import HasherSenha
from jobsync.autenticacao.domain.senha import Senha
from jobsync.autenticacao.domain.sessao_repository import SessaoRepository
from jobsync.autenticacao.domain.token_opaco import hash_token
from jobsync.autenticacao.domain.token_uso_unico import Finalidade
from jobsync.autenticacao.domain.token_uso_unico_repository import TokenUsoUnicoRepository
from jobsync.autenticacao.domain.usuario_repository import UsuarioRepository
from jobsync.shared_kernel.domain.relogio import agora_utc

logger = logging.getLogger(__name__)


@dataclass
class RedefinirSenha:
    _usuarios: UsuarioRepository
    _tokens: TokenUsoUnicoRepository
    _sessoes: SessaoRepository
    _hasher: HasherSenha
    _relogio: Callable[[], datetime] = agora_utc

    def executar(self, token: str, nova_senha: str) -> None:
        senha = Senha(nova_senha)
        consumido = self._tokens.consumir(hash_token(token), Finalidade.REDEFINICAO_SENHA, self._relogio())
        if consumido is None:
            logger.warning("token_uso_unico_invalido finalidade=%s", Finalidade.REDEFINICAO_SENHA.value)
            raise TokenInvalido("Link inválido ou expirado.")
        usuario = self._usuarios.buscar_por_id(consumido.usuario_id)
        if usuario is None:
            raise TokenInvalido("Link inválido ou expirado.")
        self._usuarios.definir_senha_hash(usuario.id, self._hasher.gerar(senha.valor))
        self._sessoes.remover_todas_do_usuario(usuario.id)
        self._tokens.remover_do_usuario(usuario.id, Finalidade.REDEFINICAO_SENHA)
        logger.info("senha_redefinida usuario_id=%s", usuario.id)
