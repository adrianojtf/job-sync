"""Entidade Sessao: autenticação ativa de um usuário, com expiração por inatividade e absoluta."""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timedelta
from uuid import UUID

from jobsync.autenticacao.domain._instantes import exigir_fuso


@dataclass(frozen=True)
class Sessao:
    """Guarda só o hash do token; o token em texto puro existe apenas no cookie."""

    token_hash: bytes
    usuario_id: UUID
    criada_em: datetime
    ultimo_acesso_em: datetime
    expira_em: datetime

    def __post_init__(self) -> None:
        if not self.token_hash:
            raise ValueError("O hash do token da sessão não pode ser vazio.")
        exigir_fuso(self.criada_em, self.ultimo_acesso_em, self.expira_em)
        if self.expira_em <= self.criada_em:
            raise ValueError("A expiração deve ser posterior à criação.")

    @classmethod
    def iniciar(
        cls, token_hash: bytes, usuario_id: UUID, agora: datetime, duracao_maxima: timedelta
    ) -> "Sessao":
        exigir_fuso(agora)
        return cls(token_hash, usuario_id, agora, agora, agora + duracao_maxima)

    def expirada(self, agora: datetime, inatividade_maxima: timedelta) -> bool:
        return agora >= self.expira_em or agora - self.ultimo_acesso_em >= inatividade_maxima

    def renovar(self, agora: datetime) -> "Sessao":
        return replace(self, ultimo_acesso_em=agora)
