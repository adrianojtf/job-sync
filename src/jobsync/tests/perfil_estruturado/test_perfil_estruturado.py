"""Testes de invariantes das entidades do Perfil Estruturado."""

import pytest

from jobsync.perfil_estruturado.domain.exceptions import ExperienciaNaoEncontrada
from jobsync.perfil_estruturado import (
    Certificacao,
    Conquista,
    DadosPerfilExtraidos,
    ExperienciaProfissional,
    FormacaoAcademica,
    Idioma,
    NivelIdioma,
    OrigemConquista,
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


def _experiencia(*conquistas: Conquista) -> ExperienciaProfissional:
    return ExperienciaProfissional(
        empresa="TechCorp", cargo="Eng. de Software", periodo="2020 - Atual", descricao="Backend.",
        conquistas=conquistas,
    )


class TestConquista:
    def test_origem_padrao_e_manual(self):
        assert Conquista("Reduzi o tempo de deploy.").origem == OrigemConquista.MANUAL

    def test_texto_vazio_levanta_erro(self):
        with pytest.raises(ValueError, match="conquista"):
            Conquista("   ")

    def test_texto_e_normalizado_sem_espacos_nas_pontas(self):
        assert Conquista("  Reduzi o tempo de deploy.  ").texto == "Reduzi o tempo de deploy."


class TestConquistasDaExperiencia:
    def test_experiencia_sem_conquistas_por_padrao(self):
        exp = ExperienciaProfissional("TechCorp", "Eng.", "2020", "Backend.")

        assert exp.conquistas == ()

    def test_conquistas_iguais_apos_normalizacao_levantam_erro(self):
        with pytest.raises(ValueError, match="duplicad"):
            _experiencia(Conquista("Reduzi o tempo de deploy."), Conquista("reduzi o tempo de DEPLOY"))

    def test_conquistas_parecidas_com_encontra_parafrase_com_caixa_e_acento(self):
        existente = Conquista("Reduzi o tempo de deploy em 40% com pipeline automatizado.")
        exp = _experiencia(existente, Conquista("Liderei a migração do banco de dados."))

        parecidas = exp.conquistas_parecidas_com("REDUZI o tempo de deploy com o pipeline automatizado")

        assert parecidas == (existente,)

    def test_conquistas_parecidas_com_nao_encontra_conquista_distinta(self):
        exp = _experiencia(Conquista("Liderei a migração do banco de dados."))

        assert exp.conquistas_parecidas_com("Construí uma API de pagamentos.") == ()


class TestComConquistaNaExperiencia:
    def _perfil_com_duas_experiencias(self) -> PerfilEstruturado:
        return _perfil_estruturado(
            experiencias=(
                _experiencia(Conquista("Reduzi o tempo de deploy.")),
                ExperienciaProfissional("Outra", "Dev", "2018", "Serviços em Go."),
            )
        )

    def test_devolve_um_perfil_novo_com_a_conquista_no_fim_da_experiencia_escolhida(self):
        perfil = self._perfil_com_duas_experiencias()
        nova = Conquista("Atuei com o cliente em um MVP.", OrigemConquista.RESPOSTA_PERGUNTA)

        atualizado = perfil.com_conquista_na_experiencia(1, nova)

        assert atualizado.experiencias[1].conquistas == (nova,)
        assert atualizado.experiencias[0] == perfil.experiencias[0]

    def test_nao_altera_o_perfil_original(self):
        perfil = self._perfil_com_duas_experiencias()

        perfil.com_conquista_na_experiencia(0, Conquista("Entreguei um MVP."))

        assert len(perfil.experiencias[0].conquistas) == 1

    def test_mantem_as_conquistas_existentes_da_experiencia(self):
        perfil = self._perfil_com_duas_experiencias()

        atualizado = perfil.com_conquista_na_experiencia(0, Conquista("Entreguei um MVP."))

        assert [c.texto for c in atualizado.experiencias[0].conquistas] == [
            "Reduzi o tempo de deploy.",
            "Entreguei um MVP.",
        ]

    @pytest.mark.parametrize("indice", [-1, 2, 10])
    def test_indice_fora_das_experiencias_levanta_erro(self, indice):
        with pytest.raises(ExperienciaNaoEncontrada):
            self._perfil_com_duas_experiencias().com_conquista_na_experiencia(indice, Conquista("Qualquer."))

    def test_conquista_duplicada_na_experiencia_levanta_erro(self):
        with pytest.raises(ValueError, match="duplicadas"):
            self._perfil_com_duas_experiencias().com_conquista_na_experiencia(
                0, Conquista("reduzi o TEMPO de deploy")
            )
