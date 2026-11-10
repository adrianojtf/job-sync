"""Implementação em memória (fake) de CandidaturaRepository para testes."""

from __future__ import annotations

from dataclasses import replace
from jobsync.shared_kernel.domain.relogio import agora_utc

from jobsync.candidatura.domain.candidatura import (
    Candidatura,
    MudancaStatus,
    StatusCandidatura,
)
from jobsync.candidatura.domain.candidatura_repository import (
    CandidaturaNaoEncontrada,
    CandidaturaRepository,
)


class CandidaturaRepositoryFake(CandidaturaRepository):
    """Fake em memória para testes de API e serviços."""

    def __init__(self) -> None:
        self._candidaturas: dict[str, Candidatura] = {}

    def salvar(self, candidatura: Candidatura) -> Candidatura:
        for existente in self._na_coluna(candidatura.perfil_identificador, candidatura.status):
            self._candidaturas[existente.id] = replace(existente, posicao=existente.posicao + 1)
        salva = replace(candidatura, posicao=0)
        self._candidaturas[salva.id] = salva
        return salva

    def listar_por_perfil(self, perfil_identificador: str) -> tuple[Candidatura, ...]:
        candidaturas = [
            c for c in self._candidaturas.values() if c.perfil_identificador == perfil_identificador
        ]
        return tuple(sorted(candidaturas, key=lambda c: c.posicao))

    def buscar_por_id(self, candidatura_id: str) -> Candidatura | None:
        return self._candidaturas.get(candidatura_id)

    def atualizar_status(
        self, candidatura_id: str, novo_status: StatusCandidatura
    ) -> Candidatura:
        candidatura = self._candidaturas.get(candidatura_id)
        if candidatura is None:
            raise CandidaturaNaoEncontrada(candidatura_id)
        ids_destino = tuple(
            c.id
            for c in self._na_coluna(candidatura.perfil_identificador, novo_status)
            if c.id != candidatura_id
        )
        return self.aplicar_movimento(candidatura_id, novo_status, (candidatura_id, *ids_destino))

    def aplicar_movimento(
        self,
        candidatura_id: str,
        novo_status: StatusCandidatura,
        ids_destino_ordenados: tuple[str, ...],
    ) -> Candidatura:
        candidatura = self._candidaturas.get(candidatura_id)
        if candidatura is None:
            raise CandidaturaNaoEncontrada(candidatura_id)

        status_origem = candidatura.status
        if status_origem != novo_status:
            nova_mudanca = MudancaStatus(novo_status, agora_utc())
            self._candidaturas[candidatura_id] = replace(
                candidatura,
                status=novo_status,
                historico_status=candidatura.historico_status + (nova_mudanca,),
            )
        self._gravar_ordem(ids_destino_ordenados)
        if status_origem != novo_status:
            restantes = self._na_coluna(candidatura.perfil_identificador, status_origem)
            self._gravar_ordem(tuple(c.id for c in restantes))
        return self._candidaturas[candidatura_id]

    def _na_coluna(self, perfil: str, status: StatusCandidatura) -> list[Candidatura]:
        return sorted(
            (
                c
                for c in self._candidaturas.values()
                if c.perfil_identificador == perfil and c.status == status
            ),
            key=lambda c: c.posicao,
        )

    def _gravar_ordem(self, ids_ordenados: tuple[str, ...]) -> None:
        for indice, id_ in enumerate(ids_ordenados):
            self._candidaturas[id_] = replace(self._candidaturas[id_], posicao=indice)
