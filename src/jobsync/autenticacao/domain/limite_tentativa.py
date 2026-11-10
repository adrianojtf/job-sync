"""Limite de tentativas de login: bloqueia temporariamente após falhas repetidas."""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timedelta
from typing import Optional

from jobsync.autenticacao.domain._instantes import exigir_fuso


@dataclass(frozen=True)
class PoliticaLimiteTentativas:
    max_falhas: int = 5
    janela: timedelta = timedelta(minutes=15)
    bloqueio: timedelta = timedelta(minutes=15)


@dataclass(frozen=True)
class LimiteTentativa:
    """Contador de falhas de uma chave (e-mail ou IP, já em forma de hash)."""

    chave: str
    contagem: int
    janela_inicia_em: datetime
    bloqueado_ate: Optional[datetime] = None

    def __post_init__(self) -> None:
        if not self.chave.strip():
            raise ValueError("A chave do limite não pode ser vazia.")
        if self.contagem < 0:
            raise ValueError("A contagem de falhas não pode ser negativa.")
        exigir_fuso(self.janela_inicia_em)

    @classmethod
    def inicial(cls, chave: str, agora: datetime) -> "LimiteTentativa":
        return cls(chave=chave, contagem=0, janela_inicia_em=agora)

    def bloqueado(self, agora: datetime) -> bool:
        return self.bloqueado_ate is not None and agora < self.bloqueado_ate

    def registrar_falha(self, agora: datetime, politica: PoliticaLimiteTentativas) -> "LimiteTentativa":
        if self.bloqueado(agora):
            return self
        if agora - self.janela_inicia_em >= politica.janela:
            atual = replace(self, contagem=0, janela_inicia_em=agora, bloqueado_ate=None)
        else:
            atual = replace(self, bloqueado_ate=None)
        contagem = atual.contagem + 1
        bloqueado_ate = agora + politica.bloqueio if contagem >= politica.max_falhas else None
        return replace(atual, contagem=contagem, bloqueado_ate=bloqueado_ate)
