"""Testes de integração do PerfilEstruturadoRepositoryImpl."""


import pytest

from jobsync.perfil.adapters.perfil_repository_impl import PerfilRepositoryImpl
from jobsync.perfil_estruturado import (
    Certificacao,
    Conquista,
    ExperienciaProfissional,
    FormacaoAcademica,
    Idioma,
    NivelIdioma,
    OrigemConquista,
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

    def test_salvar_e_buscar_perfil_com_conquistas_e_origem(self, repositorio):
        perfil = _perfil_completo(
            experiencias=(
                ExperienciaProfissional(
                    "TechCorp", "Eng. de Software", "2020-2022", "Backend em Python.",
                    conquistas=(
                        Conquista("Reduzi o tempo de deploy."),
                        Conquista("Atuei com o cliente na entrega de um MVP.", OrigemConquista.RESPOSTA_PERGUNTA),
                    ),
                ),
            )
        )

        repositorio.salvar(perfil)

        assert repositorio.buscar_por_perfil("matheus") == perfil

    def test_buscar_perfil_salvo_antes_das_conquistas_devolve_lista_vazia(self, repositorio, pool_postgres):
        with pool_postgres.connection() as conexao:
            conexao.execute(
                """
                INSERT INTO perfil_estruturado (perfil_identificador, nome_completo, email, experiencias_json)
                VALUES ('matheus', 'Matheus', 'm@example.com',
                        '[{"empresa": "TechCorp", "cargo": "Eng.", "periodo": "2020", "descricao": "Backend."}]')
                """
            )

        perfil = repositorio.buscar_por_perfil("matheus")

        assert perfil.experiencias[0].conquistas == ()


    def test_salvar_e_buscar_perfil_com_os_quatro_blocos(self, repositorio):
        perfil = _perfil_completo(
            experiencias=(
                ExperienciaProfissional(
                    "Starian", "Dev", "2024 - Atual", "",
                    conquistas=(Conquista("Atendi 1.000 usuários."),),
                    contexto="ERP para construção civil.",
                    responsabilidades=("Projetar telas", "Testar entregas"),
                    skills=("Java", "PostgreSQL"),
                ),
            )
        )

        repositorio.salvar(perfil)

        assert repositorio.buscar_por_perfil("matheus") == perfil

    def test_buscar_perfil_salvo_antes_dos_blocos_devolve_blocos_vazios(self, repositorio, pool_postgres):
        with pool_postgres.connection() as conexao:
            conexao.execute(
                """
                INSERT INTO perfil_estruturado (perfil_identificador, nome_completo, email, experiencias_json)
                VALUES ('matheus', 'Matheus', 'm@example.com',
                        '[{"empresa": "TechCorp", "cargo": "Eng.", "periodo": "2020", "descricao": "Backend."}]')
                """
            )

        experiencia = repositorio.buscar_por_perfil("matheus").experiencias[0]

        assert (experiencia.contexto, experiencia.responsabilidades, experiencia.skills) == ("", (), ())


    def test_buscar_perfil_salvo_com_periodo_e_mais_itens_fora_das_regras_novas_continua_legivel(
        self, repositorio, pool_postgres
    ):
        experiencias = ", ".join(
            f'{{"empresa": "E{n}", "cargo": "Dev", "periodo": "uns anos atrás", "descricao": ""}}' for n in range(20)
        )
        with pool_postgres.connection() as conexao:
            conexao.execute(
                f"""
                INSERT INTO perfil_estruturado (perfil_identificador, nome_completo, email, experiencias_json)
                VALUES ('matheus', 'Matheus', 'm@example.com', '[{experiencias}]')
                """
            )

        perfil = repositorio.buscar_por_perfil("matheus")

        assert len(perfil.experiencias) == 20
        assert perfil.experiencias[0].periodo == "uns anos atrás"
