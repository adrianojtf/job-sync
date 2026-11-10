"""Dublê em memória de SessaoRepository."""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from jobsync.autenticacao.domain.sessao import Sessao
from jobsync.autenticacao.domain.sessao_repository import SessaoRepository


class SessaoRepositoryFake(SessaoRepository):
    def __init__(self) -> None:
        self._sessoes: dict[bytes, Sessao] = {}

    def salvar(self, sessao: Sessao) -> None:
        self._sessoes[sessao.token_hash] = sessao

    def buscar(self, token_hash: bytes) -> Optional[Sessao]:
        return self._sessoes.get(token_hash)

    def atualizar(self, sessao: Sessao) -> None:
        self._sessoes[sessao.token_hash] = sessao

    def remover(self, token_hash: bytes) -> None:
        self._sessoes.pop(token_hash, None)

    def remover_todas_do_usuario(self, usuario_id: UUID) -> None:
        self._sessoes = {h: s for h, s in self._sessoes.items() if s.usuario_id != usuario_id}
