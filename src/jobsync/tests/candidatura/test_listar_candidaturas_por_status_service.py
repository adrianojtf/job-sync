"""Testes do caso de uso ListarCandidaturasPorStatus."""

from __future__ import annotations

from datetime import datetime

from jobsync.candidatura import Candidatura, MudancaStatus, StatusCandidatura
from jobsync.candidatura.domain.candidatura_repository import CandidaturaRepository
from jobsync.candidatura.service_layer.listar_candidaturas_por_status import ListarCandidaturasPorStatus


class CandidaturaRepositoryFake(CandidaturaRepository):
    def __init__(self, candidaturas: tuple[Candidatura, ...]):
        self._candidaturas = candidaturas

    def salvar(self, candidatura: Candidatura) -> Candidatura:
        raise NotImplementedError

    def listar_por_perfil(self, perfil_identificador: str) -> tuple[Candidatura, ...]:
        return tuple(c for c in self._candidaturas if c.perfil_identificador == perfil_identificador)

    def buscar_por_id(self, candidatura_id: str) -> Candidatura | None:
        raise NotImplementedError

    def aplicar_movimento(
        self,
        candidatura_id: str,
        novo_status: StatusCandidatura,
        ids_destino_ordenados: tuple[str, ...],
    ) -> Candidatura:
        raise NotImplementedError

    def atualizar_status(self, candidatura_id: str, novo_status: StatusCandidatura) -> Candidatura:
        raise NotImplementedError


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


class TestListarCandidaturasPorStatus:
    def test_agrupa_candidaturas_por_status(self):
        aplicado = _criar_candidatura(id="c-1", status=StatusCandidatura.APLICADO)
        entrevista = _criar_candidatura(id="c-2", status=StatusCandidatura.ENTREVISTA)
        repositorio = CandidaturaRepositoryFake(candidaturas=(aplicado, entrevista))
        use_case = ListarCandidaturasPorStatus(repositorio_candidatura=repositorio)

        resultado = use_case.executar("matheus")

        assert resultado[StatusCandidatura.APLICADO] == (aplicado,)
        assert resultado[StatusCandidatura.ENTREVISTA] == (entrevista,)

    def test_inclui_status_sem_nenhuma_candidatura(self):
        repositorio = CandidaturaRepositoryFake(candidaturas=())
        use_case = ListarCandidaturasPorStatus(repositorio_candidatura=repositorio)

        resultado = use_case.executar("matheus")

        assert set(resultado.keys()) == set(StatusCandidatura)
        assert all(candidaturas == () for candidaturas in resultado.values())

    def test_ignora_candidaturas_de_outro_perfil(self):
        candidatura_outra_pessoa = _criar_candidatura(id="c-outra", perfil_identificador="outra-pessoa")
        repositorio = CandidaturaRepositoryFake(candidaturas=(candidatura_outra_pessoa,))
        use_case = ListarCandidaturasPorStatus(repositorio_candidatura=repositorio)

        resultado = use_case.executar("matheus")

        assert resultado[StatusCandidatura.APLICADO] == ()
