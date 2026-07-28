"""Testes de invariantes das entidades do Perfil Estruturado."""

import pytest

from domain.perfil_estruturado import (
    Certificacao,
    DadosPerfilExtraidos,
    ExperienciaProfissional,
    FormacaoAcademica,
    Idioma,
    NivelIdioma,
    PerfilEstruturado,
)


def _perfil_estruturado(**overrides) -> PerfilEstruturado:
    dados = dict(
        perfil_identificador="matheus",
        nome_completo="Matheus Henrique Moreira",
        email="matheus@example.com",
        linkedin="linkedin.com/in/matheus",
        resumo_profissional="Product Manager com experiência em SaaS.",
        experiencias=(),
        formacoes=(),
        certificacoes=(),
        idiomas=(),
        tecnologias=(),
    )
    dados.update(overrides)
    return PerfilEstruturado(**dados)


class TestExperienciaProfissional:
    def test_criar_valida(self):
        exp = ExperienciaProfissional(
            empresa="TechCorp", cargo="Eng. de Software", periodo="2020 - Atual", descricao="Backend."
        )
        assert exp.empresa == "TechCorp"

    def test_empresa_vazia_levanta_erro(self):
        with pytest.raises(ValueError):
            ExperienciaProfissional(empresa="", cargo="Eng.", periodo="2020", descricao="x")

    def test_cargo_vazio_levanta_erro(self):
        with pytest.raises(ValueError):
            ExperienciaProfissional(empresa="TechCorp", cargo="", periodo="2020", descricao="x")


class TestFormacaoAcademica:
    def test_criar_valida(self):
        formacao = FormacaoAcademica(instituicao="USP", curso="Ciência da Computação", periodo="2016-2020")
        assert formacao.instituicao == "USP"

    def test_instituicao_vazia_levanta_erro(self):
        with pytest.raises(ValueError):
            FormacaoAcademica(instituicao="", curso="ADS", periodo="2020")

    def test_curso_vazio_levanta_erro(self):
        with pytest.raises(ValueError):
            FormacaoAcademica(instituicao="USP", curso="", periodo="2020")


class TestCertificacao:
    def test_criar_valida(self):
        cert = Certificacao(nome="AWS Certified", instituicao="Amazon", ano="2023")
        assert cert.nome == "AWS Certified"

    def test_nome_vazio_levanta_erro(self):
        with pytest.raises(ValueError):
            Certificacao(nome="", instituicao="Amazon", ano="2023")


class TestIdioma:
    def test_criar_valido(self):
        idioma = Idioma(idioma="Inglês", nivel=NivelIdioma.AVANCADO)
        assert idioma.nivel == NivelIdioma.AVANCADO

    def test_idioma_vazio_levanta_erro(self):
        with pytest.raises(ValueError):
            Idioma(idioma="", nivel=NivelIdioma.BASICO)


class TestPerfilEstruturado:
    def test_criar_perfil_valido_com_listas_vazias(self):
        perfil = _perfil_estruturado()

        assert perfil.perfil_identificador == "matheus"
        assert perfil.experiencias == ()

    def test_criar_perfil_com_multiplas_entradas(self):
        perfil = _perfil_estruturado(
            experiencias=(
                ExperienciaProfissional("TechCorp", "Eng.", "2020-2022", "Backend"),
                ExperienciaProfissional("OutraEmpresa", "Sr Eng.", "2022-Atual", "Full stack"),
            ),
            idiomas=(Idioma("Inglês", NivelIdioma.FLUENTE),),
            tecnologias=("Python", "Docker"),
        )

        assert len(perfil.experiencias) == 2
        assert perfil.tecnologias == ("Python", "Docker")

    def test_identificador_vazio_levanta_erro(self):
        with pytest.raises(ValueError):
            _perfil_estruturado(perfil_identificador="")

    def test_nome_completo_vazio_levanta_erro(self):
        with pytest.raises(ValueError):
            _perfil_estruturado(nome_completo="")

    def test_email_vazio_levanta_erro(self):
        with pytest.raises(ValueError):
            _perfil_estruturado(email="")


class TestDadosPerfilExtraidos:
    def test_criar_sem_identificador(self):
        dados = DadosPerfilExtraidos(
            nome_completo="",
            email="",
            linkedin="",
            resumo_profissional="",
            experiencias=(),
            formacoes=(),
            certificacoes=(),
            idiomas=(),
            tecnologias=(),
        )

        assert dados.nome_completo == ""
        assert not hasattr(dados, "perfil_identificador")
