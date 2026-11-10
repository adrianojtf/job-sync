"""Dublê em memória de LimiteTentativasRepository."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from jobsync.autenticacao.domain.limite_tentativa import LimiteTentativa, PoliticaLimiteTentativas
from jobsync.autenticacao.domain.limite_tentativas_repository import LimiteTentativasRepository


class LimiteTentativasRepositoryFake(LimiteTentativasRepository):
    def __init__(self) -> None:
        self._limites: dict[str, LimiteTentativa] = {}

    def obter(self, chave: str) -> Optional[LimiteTentativa]:
        return self._limites.get(chave)

    def registrar_falha(
        self, chave: str, agora: datetime, politica: PoliticaLimiteTentativas
    ) -> LimiteTentativa:
        atual = self._limites.get(chave) or LimiteTentativa.inicial(chave, agora)
        atualizado = atual.registrar_falha(agora, politica)
        self._limites[chave] = atualizado
        return atualizado

    def limpar(self, chave: str) -> None:
        self._limites.pop(chave, None)
