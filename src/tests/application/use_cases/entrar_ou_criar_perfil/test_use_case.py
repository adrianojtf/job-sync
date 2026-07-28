"""Testes do caso de uso EntrarOuCriarPerfil."""
from typing import Optional

from application.use_cases.entrar_ou_criar_perfil import EntrarOuCriarPerfil
from domain.perfil import Perfil
from domain.perfil.perfil_repository import PerfilRepository


class PerfilRepositoryFake(PerfilRepository):
    def __init__(self, perfis_existentes: tuple[Perfil, ...] = ()):
        self._perfis: dict[str, Perfil] = {p.identificador: p for p in perfis_existentes}
        self.chamou_criar_com: Optional[str] = None

    def buscar_por_identificador(self, identificador: str) -> Optional[Perfil]:
        return self._perfis.get(identificador)

    def criar(self, identificador: str) -> Perfil:
        self.chamou_criar_com = identificador
        perfil = Perfil(identificador=identificador)
        self._perfis[identificador] = perfil
        return perfil


class TestEntrarOuCriarPerfil:
    def test_identificador_novo_cria_perfil(self):
        repositorio = PerfilRepositoryFake()
        use_case = EntrarOuCriarPerfil(repositorio_perfil=repositorio)

        perfil = use_case.executar("matheus")

        assert perfil.identificador == "matheus"
        assert repositorio.chamou_criar_com == "matheus"

    def test_identificador_existente_retorna_perfil_sem_criar_novamente(self):
        perfil_existente = Perfil(identificador="matheus")
        repositorio = PerfilRepositoryFake(perfis_existentes=(perfil_existente,))
        use_case = EntrarOuCriarPerfil(repositorio_perfil=repositorio)

        perfil = use_case.executar("matheus")

        assert perfil == perfil_existente
        assert repositorio.chamou_criar_com is None
