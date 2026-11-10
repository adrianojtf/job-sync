"""Caso de uso: descobre o usuário de uma sessão a partir do token do cookie."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Optional

from jobsync.autenticacao.domain.configuracao import ConfiguracaoAutenticacao
from jobsync.autenticacao.domain.sessao_repository import SessaoRepository
from jobsync.autenticacao.domain.token_opaco import hash_token
from jobsync.autenticacao.domain.usuario import Usuario
from jobsync.autenticacao.domain.usuario_repository import UsuarioRepository
from jobsync.shared_kernel.domain.relogio import agora_utc


@dataclass
class ResolverSessao:
    _usuarios: UsuarioRepository
    _sessoes: SessaoRepository
    _config: ConfiguracaoAutenticacao
    _relogio: Callable[[], datetime] = agora_utc

    def executar(self, token: Optional[str]) -> Optional[Usuario]:
        if not token:
            return None
        token_hash = hash_token(token)
        sessao = self._sessoes.buscar(token_hash)
        if sessao is None:
            return None
        agora = self._relogio()
        if sessao.expirada(agora, self._config.sessao_inatividade):
            self._sessoes.remover(token_hash)
            return None
        usuario = self._usuarios.buscar_por_id(sessao.usuario_id)
        if usuario is None:
            self._sessoes.remover(token_hash)
            return None
        if agora - sessao.ultimo_acesso_em >= self._config.sessao_renovacao_minima:
            self._sessoes.atualizar(sessao.renovar(agora))
        return usuario
