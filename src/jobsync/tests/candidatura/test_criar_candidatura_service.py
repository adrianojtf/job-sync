"""Testes do caso de uso CriarCandidatura."""

from __future__ import annotations

from jobsync.candidatura import Candidatura, StatusCandidatura
from jobsync.candidatura.domain.candidatura_repository import CandidaturaRepository
from jobsync.candidatura.service_layer.criar_candidatura import CriarCandidatura, CriarCandidaturaInputDto
from jobsync.vaga import Vaga
from jobsync.vaga.domain.vaga_repository import VagaRepository


class CandidaturaRepositoryFake(CandidaturaRepository):
    def __init__(self) -> None:
        self.candidaturas_salvas: list[Candidatura] = []

    def salvar(self, candidatura: Candidatura) -> Candidatura:
        self.candidaturas_salvas.append(candidatura)
        return candidatura

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
        raise NotImplementedError


class VagaRepositoryFake(VagaRepository):
    def __init__(self) -> None:
        self.vagas_marcadas_convertidas: list[str] = []

    def salvar(self, vaga: Vaga) -> Vaga:
        raise NotImplementedError

    def listar_nao_convertidas(self, perfil_identificador: str) -> tuple[Vaga, ...]:
        raise NotImplementedError

    def marcar_como_convertida(self, vaga_id: str) -> None:
        self.vagas_marcadas_convertidas.append(vaga_id)


class TestCriarCandidatura:
    def test_cria_candidatura_com_status_inicial_aplicado(self):
        repositorio_candidatura = CandidaturaRepositoryFake()
        repositorio_vaga = VagaRepositoryFake()
        use_case = CriarCandidatura(
            repositorio_candidatura=repositorio_candidatura, repositorio_vaga=repositorio_vaga
        )

        candidatura = use_case.executar(
            CriarCandidaturaInputDto(
                perfil_identificador="matheus",
                vaga_id="vaga-1",
                curriculo_salvo_id="curriculo-1",
                empresa="TechCorp",
                cargo="Engenheiro de Software",
            )
        )

        assert candidatura.status == StatusCandidatura.APLICADO
        assert candidatura.id
        assert repositorio_candidatura.candidaturas_salvas == [candidatura]

    def test_marca_vaga_como_convertida(self):
        repositorio_candidatura = CandidaturaRepositoryFake()
        repositorio_vaga = VagaRepositoryFake()
        use_case = CriarCandidatura(
            repositorio_candidatura=repositorio_candidatura, repositorio_vaga=repositorio_vaga
        )

        use_case.executar(
            CriarCandidaturaInputDto(
                perfil_identificador="matheus",
                vaga_id="vaga-1",
                curriculo_salvo_id="curriculo-1",
                empresa="TechCorp",
                cargo="Engenheiro de Software",
            )
        )

        assert repositorio_vaga.vagas_marcadas_convertidas == ["vaga-1"]
