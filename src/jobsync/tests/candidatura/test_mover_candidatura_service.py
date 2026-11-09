"""Testes do caso de uso MoverCandidatura."""

from dataclasses import replace
from datetime import datetime

from jobsync.candidatura import Candidatura, MudancaStatus, StatusCandidatura
from jobsync.candidatura.domain.candidatura_repository import CandidaturaRepository
from jobsync.candidatura.service_layer.mover_candidatura import MoverCandidatura


class CandidaturaRepositoryFake(CandidaturaRepository):
    def __init__(self, candidatura: Candidatura):
        self._candidatura = candidatura
        self.chamada: tuple[str, StatusCandidatura] | None = None

    def salvar(self, candidatura: Candidatura) -> Candidatura:
        raise NotImplementedError

    def listar_por_perfil(self, perfil_identificador: str) -> tuple[Candidatura, ...]:
        raise NotImplementedError

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
        self.chamada = (candidatura_id, novo_status)
        return replace(
            self._candidatura,
            status=novo_status,
            historico_status=(MudancaStatus(status=novo_status, data=datetime.now()),),
        )


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


class TestMoverCandidatura:
    def test_atualiza_status_via_repositorio(self):
        candidatura = _criar_candidatura()
        repositorio = CandidaturaRepositoryFake(candidatura)
        use_case = MoverCandidatura(repositorio_candidatura=repositorio)

        resultado = use_case.executar(candidatura.id, StatusCandidatura.ENTREVISTA)

        assert repositorio.chamada == (candidatura.id, StatusCandidatura.ENTREVISTA)
        assert resultado.status == StatusCandidatura.ENTREVISTA

    def test_aceita_qualquer_transicao_entre_colunas(self):
        candidatura = _criar_candidatura(status=StatusCandidatura.OFERTA)
        repositorio = CandidaturaRepositoryFake(candidatura)
        use_case = MoverCandidatura(repositorio_candidatura=repositorio)

        resultado = use_case.executar(candidatura.id, StatusCandidatura.APLICADO)

        assert resultado.status == StatusCandidatura.APLICADO
