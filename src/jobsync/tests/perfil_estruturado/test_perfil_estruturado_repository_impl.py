"""Testes de integração do PerfilEstruturadoRepositoryImpl."""


import pytest

from jobsync.perfil.adapters.perfil_repository_impl import PerfilRepositoryImpl
from jobsync.perfil_estruturado import (
    Certificacao,
    ExperienciaProfissional,
    FormacaoAcademica,
    Idioma,
    NivelIdioma,
    PerfilEstruturado,
)
from jobsync.perfil_estruturado.adapters import PerfilEstruturadoRepositoryImpl


@pytest.fixture
def repositorio(pool_postgres):
    PerfilRepositoryImpl(pool_postgres).criar("matheus")
    return PerfilEstruturadoRepositoryImpl(pool_postgres)


def _perfil_completo(**overrides) -> PerfilEstruturado:
    dados = dict(
        perfil_identificador="matheus",
        nome_completo="Matheus Henrique Moreira",
        email="matheus@example.com",
        linkedin="linkedin.com/in/matheus",
        resumo_profissional="Product Manager com experiência em SaaS.",
        experiencias=(
            ExperienciaProfissional("TechCorp", "Eng. de Software", "2020-2022", "Backend em Python."),
            ExperienciaProfissional("OutraEmpresa", "PM Sênior", "2022-Atual", "Produto B2B."),
        ),
        formacoes=(FormacaoAcademica("USP", "Ciência da Computação", "2016-2020"),),
        certificacoes=(Certificacao("AWS Certified", "Amazon", "2023"),),
        idiomas=(Idioma("Inglês", NivelIdioma.FLUENTE), Idioma("Espanhol", NivelIdioma.BASICO)),
        tecnologias=("Python", "SQL", "Docker"),
    )
    dados.update(overrides)
    return PerfilEstruturado(**dados)


class TestPerfilEstruturadoRepositoryImpl:
    def test_salvar_e_buscar_perfil_completo(self, repositorio):
        perfil = _perfil_completo()

        repositorio.salvar(perfil)

        assert repositorio.buscar_por_perfil("matheus") == perfil

    def test_salvar_e_buscar_perfil_com_listas_vazias(self, repositorio):
        perfil = _perfil_completo(
            experiencias=(), formacoes=(), certificacoes=(), idiomas=(), tecnologias=()
        )

        repositorio.salvar(perfil)

        assert repositorio.buscar_por_perfil("matheus") == perfil

    def test_salvar_duas_vezes_atualiza_sem_duplicar(self, repositorio, pool_postgres):
        perfil_v1 = _perfil_completo(resumo_profissional="Versão 1")
        perfil_v2 = _perfil_completo(resumo_profissional="Versão 2")

        repositorio.salvar(perfil_v1)
        repositorio.salvar(perfil_v2)

        resultado = repositorio.buscar_por_perfil("matheus")
        assert resultado.resumo_profissional == "Versão 2"

        with pool_postgres.connection() as conexao:
            total = conexao.execute(
                "SELECT COUNT(*) FROM perfil_estruturado WHERE perfil_identificador = %s", ("matheus",)
            ).fetchone()[0]
        assert total == 1

    def test_buscar_perfil_inexistente_retorna_none(self, repositorio):
        assert repositorio.buscar_por_perfil("nao-existe") is None
