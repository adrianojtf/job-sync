"""Testes do Domain Service MontarCurriculoDoPerfilEstruturado."""

from domain.curriculo import TipoSecao
from domain.perfil_estruturado import (
    Certificacao,
    ExperienciaProfissional,
    FormacaoAcademica,
    Idioma,
    NivelIdioma,
    PerfilEstruturado,
)
from domain.perfil_estruturado.montar_curriculo_do_perfil_estruturado_service import (
    MontarCurriculoDoPerfilEstruturado,
)


def _perfil_vazio(**overrides) -> PerfilEstruturado:
    dados = dict(
        perfil_identificador="matheus",
        nome_completo="Matheus Henrique Moreira",
        email="matheus@example.com",
        linkedin="linkedin.com/in/matheus",
        resumo_profissional="",
        experiencias=(),
        formacoes=(),
        certificacoes=(),
        idiomas=(),
        tecnologias=(),
    )
    dados.update(overrides)
    return PerfilEstruturado(**dados)


class TestMontarCurriculoDoPerfilEstruturado:
    def test_perfil_completo_gera_todas_as_secoes(self):
        perfil = _perfil_vazio(
            resumo_profissional="Product Manager com experiência em SaaS.",
            experiencias=(ExperienciaProfissional("TechCorp", "Eng.", "2020-2022", "Backend."),),
            formacoes=(FormacaoAcademica("USP", "Ciência da Computação", "2016-2020"),),
            certificacoes=(Certificacao("AWS Certified", "Amazon", "2023"),),
            idiomas=(Idioma("Inglês", NivelIdioma.FLUENTE),),
            tecnologias=("Python", "Docker"),
        )

        curriculo = MontarCurriculoDoPerfilEstruturado().executar(perfil)

        assert curriculo is not None
        assert curriculo.nome_completo == "Matheus Henrique Moreira"
        assert curriculo.obter_secao(TipoSecao.PERFIL).conteudo == "Product Manager com experiência em SaaS."
        assert "TechCorp" in curriculo.obter_secao(TipoSecao.EXPERIENCIAS).conteudo
        assert "USP" in curriculo.obter_secao(TipoSecao.FORMACAO).conteudo
        assert "AWS Certified" in curriculo.obter_secao(TipoSecao.CERTIFICACOES).conteudo
        assert "Fluente" in curriculo.obter_secao(TipoSecao.IDIOMAS).conteudo
        assert curriculo.obter_secao(TipoSecao.TECNOLOGIAS).conteudo == "Python, Docker"

    def test_perfil_parcial_gera_so_as_secoes_com_conteudo(self):
        perfil = _perfil_vazio(
            resumo_profissional="Resumo qualquer.",
            tecnologias=("Python",),
        )

        curriculo = MontarCurriculoDoPerfilEstruturado().executar(perfil)

        assert curriculo is not None
        assert curriculo.obter_secao(TipoSecao.PERFIL) is not None
        assert curriculo.obter_secao(TipoSecao.TECNOLOGIAS) is not None
        assert curriculo.obter_secao(TipoSecao.EXPERIENCIAS) is None
        assert curriculo.obter_secao(TipoSecao.FORMACAO) is None

    def test_perfil_sem_nenhum_conteudo_retorna_none(self):
        perfil = _perfil_vazio()

        curriculo = MontarCurriculoDoPerfilEstruturado().executar(perfil)

        assert curriculo is None
