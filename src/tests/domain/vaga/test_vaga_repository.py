"""Testes de porta para o repositório de vagas capturadas."""

from datetime import datetime

from domain.vaga import Vaga
from domain.vaga.vaga_repository import VagaRepository


class VagaRepositoryFake(VagaRepository):
    def __init__(self) -> None:
        self._vagas: dict[str, Vaga] = {}
        self._convertidas: set[str] = set()

    def salvar(self, vaga: Vaga) -> Vaga:
        self._vagas[vaga.id] = vaga
        return vaga

    def listar_nao_convertidas(self, perfil_identificador: str) -> tuple[Vaga, ...]:
        return tuple(
            v
            for v in self._vagas.values()
            if v.perfil_identificador == perfil_identificador and v.id not in self._convertidas
        )

    def marcar_como_convertida(self, vaga_id: str) -> None:
        self._convertidas.add(vaga_id)


def _criar_vaga(**overrides) -> Vaga:
    dados = dict(
        id="vaga-1",
        perfil_identificador="matheus",
        texto_descricao="Vaga qualquer",
        data_captura=datetime(2026, 7, 26),
    )
    dados.update(overrides)
    return Vaga(**dados)


def test_vaga_repository_eh_interface_pura() -> None:
    fake = VagaRepositoryFake()
    vaga = _criar_vaga()

    fake.salvar(vaga)

    assert fake.listar_nao_convertidas("matheus") == (vaga,)

    fake.marcar_como_convertida(vaga.id)

    assert fake.listar_nao_convertidas("matheus") == ()
