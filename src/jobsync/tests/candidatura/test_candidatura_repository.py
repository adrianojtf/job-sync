"""Testes de porta para o repositório de candidaturas."""

from dataclasses import replace
from datetime import datetime

from jobsync.candidatura import Candidatura, MudancaStatus, StatusCandidatura
from jobsync.candidatura.domain.candidatura_repository import CandidaturaRepository


class CandidaturaRepositoryFake(CandidaturaRepository):
    def __init__(self) -> None:
        self._candidaturas: dict[str, Candidatura] = {}

    def salvar(self, candidatura: Candidatura) -> Candidatura:
        self._candidaturas[candidatura.id] = candidatura
        return candidatura

    def listar_por_perfil(self, perfil_identificador: str) -> tuple[Candidatura, ...]:
        return tuple(c for c in self._candidaturas.values() if c.perfil_identificador == perfil_identificador)

    def atualizar_status(self, candidatura_id: str, novo_status: StatusCandidatura) -> Candidatura:
        atual = self._candidaturas[candidatura_id]
        atualizada = replace(
            atual,
            status=novo_status,
            historico_status=(MudancaStatus(status=novo_status, data=datetime.now()),),
        )
        self._candidaturas[candidatura_id] = atualizada
        return atualizada


def _criar_candidatura(**overrides) -> Candidatura:
    dados = dict(
        id="candidatura-1",
        perfil_identificador="matheus",
        vaga_id="vaga-1",
        curriculo_salvo_id="curriculo-1",
        empresa="TechCorp",
        cargo="Engenheiro de Software",
        status=StatusCandidatura.APLICADO,
        data_aplicacao=datetime(2026, 7, 26),
        historico_status=(MudancaStatus(status=StatusCandidatura.APLICADO, data=datetime(2026, 7, 26)),),
    )
    dados.update(overrides)
    return Candidatura(**dados)


def test_candidatura_repository_eh_interface_pura() -> None:
    fake = CandidaturaRepositoryFake()
    candidatura = _criar_candidatura()

    fake.salvar(candidatura)

    assert fake.listar_por_perfil("matheus") == (candidatura,)

    atualizada = fake.atualizar_status(candidatura.id, StatusCandidatura.ENTREVISTA)

    assert atualizada.status == StatusCandidatura.ENTREVISTA
