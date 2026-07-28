"""Testes do caso de uso SalvarPerfilEstruturado."""

import pytest

from application.use_cases.salvar_perfil_estruturado import (
    SalvarPerfilEstruturado,
    SalvarPerfilEstruturadoInputDto,
)
from domain.perfil_estruturado import PerfilEstruturado
from domain.perfil_estruturado.perfil_estruturado_repository import PerfilEstruturadoRepository


class RepositorioFake(PerfilEstruturadoRepository):
    def __init__(self):
        self.perfil_salvo: PerfilEstruturado | None = None

    def salvar(self, perfil: PerfilEstruturado) -> PerfilEstruturado:
        self.perfil_salvo = perfil
        return perfil

    def buscar_por_perfil(self, perfil_identificador: str) -> PerfilEstruturado | None:
        return self.perfil_salvo


def _input_dto(**overrides) -> SalvarPerfilEstruturadoInputDto:
    dados = dict(
        perfil_identificador="matheus",
        nome_completo="Matheus Henrique Moreira",
        email="matheus@example.com",
        linkedin="linkedin.com/in/matheus",
        resumo_profissional="Resumo qualquer.",
        experiencias=(),
        formacoes=(),
        certificacoes=(),
        idiomas=(),
        tecnologias=(),
    )
    dados.update(overrides)
    return SalvarPerfilEstruturadoInputDto(**dados)


class TestSalvarPerfilEstruturado:
    def test_salva_perfil_valido(self):
        repositorio = RepositorioFake()
        use_case = SalvarPerfilEstruturado(repositorio=repositorio)

        resultado = use_case.executar(_input_dto())

        assert repositorio.perfil_salvo == resultado
        assert resultado.perfil_identificador == "matheus"

    def test_identificador_vazio_gera_erro(self):
        use_case = SalvarPerfilEstruturado(repositorio=RepositorioFake())

        with pytest.raises(ValueError, match="identificador"):
            use_case.executar(_input_dto(perfil_identificador=""))

    def test_nome_completo_vazio_gera_erro(self):
        use_case = SalvarPerfilEstruturado(repositorio=RepositorioFake())

        with pytest.raises(ValueError, match="nome completo"):
            use_case.executar(_input_dto(nome_completo=""))

    def test_email_vazio_gera_erro(self):
        use_case = SalvarPerfilEstruturado(repositorio=RepositorioFake())

        with pytest.raises(ValueError, match="email"):
            use_case.executar(_input_dto(email=""))
