"""Caso de uso: abre uma sessão para um usuário já autenticado por qualquer método."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Callable
from uuid import UUID

from jobsync.autenticacao.domain.configuracao import ConfiguracaoAutenticacao
from jobsync.autenticacao.domain.sessao import Sessao
from jobsync.autenticacao.domain.sessao_repository import SessaoRepository
from jobsync.autenticacao.domain.token_opaco import gerar_token, hash_token
from jobsync.shared_kernel.domain.relogio import agora_utc


@dataclass
class EmitirSessao:
    _sessoes: SessaoRepository
    _config: ConfiguracaoAutenticacao
    _relogio: Callable[[], datetime] = agora_utc

    def executar(self, usuario_id: UUID) -> str:
        """Devolve o token em texto puro (vai só para o cookie); o banco guarda o hash."""
        token = gerar_token()
        sessao = Sessao.iniciar(hash_token(token), usuario_id, self._relogio(), self._config.sessao_maxima)
        self._sessoes.salvar(sessao)
        return token
