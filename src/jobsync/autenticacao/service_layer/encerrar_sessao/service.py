"""Caso de uso: logout. Encerrar uma sessão inexistente não é erro."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from jobsync.autenticacao.domain.sessao_repository import SessaoRepository
from jobsync.autenticacao.domain.token_opaco import hash_token

logger = logging.getLogger(__name__)


@dataclass
class EncerrarSessao:
    _sessoes: SessaoRepository

    def executar(self, token: Optional[str]) -> None:
        if not token:
            return
        self._sessoes.remover(hash_token(token))
        logger.info("sessao_encerrada")
