"""Testes do caso de uso BuscarPerfilEstruturado."""

from application.use_cases.buscar_perfil_estruturado import BuscarPerfilEstruturado
from domain.perfil_estruturado import PerfilEstruturado
from domain.perfil_estruturado.perfil_estruturado_repository import PerfilEstruturadoRepository


class RepositorioFake(PerfilEstruturadoRepository):
    def __init__(self, perfil: PerfilEstruturado | None = None):
        self._perfil = perfil

    def salvar(self, perfil: PerfilEstruturado) -> PerfilEstruturado:
        raise NotImplementedError

    def buscar_por_perfil(self, perfil_identificador: str) -> PerfilEstruturado | None:
        return self._perfil


def _perfil() -> PerfilEstruturado:
    return PerfilEstruturado(
        perfil_identificador="matheus",
        nome_completo="Matheus Henrique Moreira",
        email="matheus@example.com",
        linkedin="linkedin.com/in/matheus",
        resumo_profissional="Resumo.",
        experiencias=(),
        formacoes=(),
        certificacoes=(),
        idiomas=(),
        tecnologias=(),
    )


class TestBuscarPerfilEstruturado:
    def test_retorna_perfil_existente(self):
        use_case = BuscarPerfilEstruturado(repositorio=RepositorioFake(_perfil()))

        assert use_case.executar("matheus") == _perfil()

    def test_retorna_none_quando_nao_existe(self):
        use_case = BuscarPerfilEstruturado(repositorio=RepositorioFake(None))

        assert use_case.executar("matheus") is None
