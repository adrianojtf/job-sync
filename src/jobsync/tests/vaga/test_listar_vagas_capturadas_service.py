"""Testes do caso de uso ListarVagasCapturadas."""

from datetime import datetime

from jobsync.vaga import Vaga
from jobsync.vaga.domain.vaga_repository import VagaRepository
from jobsync.vaga.service_layer.listar_vagas_capturadas import ListarVagasCapturadas


class VagaRepositoryFake(VagaRepository):
    def __init__(self, vagas: tuple[Vaga, ...]):
        self._vagas = vagas

    def salvar(self, vaga: Vaga) -> Vaga:
        raise NotImplementedError

    def listar_nao_convertidas(self, perfil_identificador: str) -> tuple[Vaga, ...]:
        return tuple(v for v in self._vagas if v.perfil_identificador == perfil_identificador)

    def marcar_como_convertida(self, vaga_id: str) -> None:
        raise NotImplementedError


def _criar_vaga(**overrides) -> Vaga:
    dados = dict(
        id="vaga-1",
        perfil_identificador="matheus",
        texto_descricao="Vaga qualquer",
        data_captura=datetime(2026, 7, 26),
    )
    dados.update(overrides)
    return Vaga(**dados)


class TestListarVagasCapturadas:
    def test_lista_apenas_vagas_do_perfil_informado(self):
        vaga_matheus = _criar_vaga(id="vaga-matheus", perfil_identificador="matheus")
        vaga_outra = _criar_vaga(id="vaga-outra", perfil_identificador="outra-pessoa")
        repositorio = VagaRepositoryFake(vagas=(vaga_matheus, vaga_outra))
        use_case = ListarVagasCapturadas(repositorio)

        resultado = use_case.executar("matheus")

        assert resultado == (vaga_matheus,)
