"""Testes de porta para o repositório de perfis."""

from typing import Optional

from jobsync.perfil import Perfil, PerfilRepository


class PerfilRepositoryFake(PerfilRepository):
    def __init__(self) -> None:
        self._perfis: dict[str, Perfil] = {}

    def buscar_por_identificador(self, identificador: str) -> Optional[Perfil]:
        return self._perfis.get(identificador)

    def criar(self, identificador: str) -> Perfil:
        perfil = Perfil(identificador=identificador)
        self._perfis[identificador] = perfil
        return perfil


def test_perfil_repository_eh_interface_pura() -> None:
    fake = PerfilRepositoryFake()

    assert fake.buscar_por_identificador("matheus") is None

    criado = fake.criar("matheus")

    assert isinstance(criado, Perfil)
    assert fake.buscar_por_identificador("matheus") == criado
