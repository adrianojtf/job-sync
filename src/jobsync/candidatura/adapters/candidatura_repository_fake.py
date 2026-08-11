"""Implementação em memória (fake) de CandidaturaRepository para testes."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime

from jobsync.candidatura.domain.candidatura import (
    Candidatura,
    MudancaStatus,
    StatusCandidatura,
)
from jobsync.candidatura.domain.candidatura_repository import CandidaturaRepository


class CandidaturaRepositoryFake(CandidaturaRepository):
    """Fake em memória para testes de API e serviços."""

    def __init__(self) -> None:
        self._candidaturas: dict[str, Candidatura] = {}

    def salvar(self, candidatura: Candidatura) -> Candidatura:
        self._candidaturas[candidatura.id] = candidatura
        return candidatura

    def listar_por_perfil(self, perfil_identificador: str) -> tuple[Candidatura, ...]:
        return tuple(
            c
            for c in self._candidaturas.values()
            if c.perfil_identificador == perfil_identificador
        )

    def atualizar_status(
        self, candidatura_id: str, novo_status: StatusCandidatura
    ) -> Candidatura:
        candidatura = self._candidaturas.get(candidatura_id)
        if candidatura is None:
            raise ValueError("Candidatura não encontrada.")

        nova_mudanca = MudancaStatus(novo_status, datetime.now())
        nova_candidatura = replace(
            candidatura,
            status=novo_status,
            historico_status=candidatura.historico_status + (nova_mudanca,),
        )
        self._candidaturas[candidatura_id] = nova_candidatura
        return nova_candidatura
