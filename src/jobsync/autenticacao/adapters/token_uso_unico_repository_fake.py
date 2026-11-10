"""Dublê em memória de TokenUsoUnicoRepository."""
from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from jobsync.autenticacao.domain.token_uso_unico import Finalidade, TokenUsoUnico
from jobsync.autenticacao.domain.token_uso_unico_repository import TokenUsoUnicoRepository


class TokenUsoUnicoRepositoryFake(TokenUsoUnicoRepository):
    def __init__(self) -> None:
        self._tokens: dict[bytes, TokenUsoUnico] = {}

    def salvar(self, token: TokenUsoUnico) -> None:
        self._tokens[token.token_hash] = token

    def consumir(
        self, token_hash: bytes, finalidade: Finalidade, agora: datetime
    ) -> Optional[TokenUsoUnico]:
        token = self._tokens.get(token_hash)
        if token is None or token.finalidade is not finalidade or not token.utilizavel(agora):
            return None
        usado = token.marcar_usado(agora)
        self._tokens[token_hash] = usado
        return usado

    def remover_do_usuario(self, usuario_id: UUID, finalidade: Finalidade) -> None:
        self._tokens = {
            h: t
            for h, t in self._tokens.items()
            if not (t.usuario_id == usuario_id and t.finalidade is finalidade)
        }
