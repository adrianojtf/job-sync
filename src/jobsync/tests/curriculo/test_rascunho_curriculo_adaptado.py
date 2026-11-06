"""Testes do agregado RascunhoCurriculoAdaptado."""
import pytest

from jobsync.curriculo import (
    ExperienciaParaAvaliacao,
    RascunhoCurriculoAdaptado,
    SecaoCurriculo,
    TipoSecao,
)


def _experiencia(
    cargo: str = "Engenheiro de Software",
    empresa: str = "Starian",
    periodo: str = "2022 - Atual",
    descricao: str = "Desenvolvi APIs em Java.",
) -> ExperienciaParaAvaliacao:
    return ExperienciaParaAvaliacao(
        cargo=cargo, empresa=empresa, periodo=periodo, descricao=descricao
    )


def _secao_perfil() -> SecaoCurriculo:
    return SecaoCurriculo(TipoSecao.PERFIL, "Perfil", "Engenheiro backend.")


class TestRascunhoCurriculoAdaptado:
    def test_nome_completo_vazio_gera_erro(self):
        with pytest.raises(ValueError, match="nome completo"):
            RascunhoCurriculoAdaptado(
                nome_completo="  ",
                email="ana@ex.com",
                linkedin="",
                secoes=(_secao_perfil(),),
            )

    def test_rascunho_sem_secoes_e_sem_experiencias_gera_erro(self):
        with pytest.raises(ValueError, match="ao menos uma seção"):
            RascunhoCurriculoAdaptado(
                nome_completo="Ana Souza",
                email="ana@ex.com",
                linkedin="",
                secoes=(),
                experiencias=(),
            )

    def test_secao_de_experiencias_com_experiencias_estruturadas_gera_erro(self):
        with pytest.raises(ValueError, match="experiências"):
            RascunhoCurriculoAdaptado(
                nome_completo="Ana Souza",
                email="ana@ex.com",
                linkedin="",
                secoes=(SecaoCurriculo(TipoSecao.EXPERIENCIAS, "Experiências", "texto"),),
                experiencias=(_experiencia(),),
            )

    def test_experiencia_estruturada_sem_cargo_gera_erro(self):
        with pytest.raises(ValueError, match="cargo"):
            RascunhoCurriculoAdaptado(
                nome_completo="Ana Souza",
                email="ana@ex.com",
                linkedin="",
                secoes=(),
                experiencias=(_experiencia(cargo=" "),),
            )

    def test_experiencia_estruturada_sem_empresa_gera_erro(self):
        with pytest.raises(ValueError, match="empresa"):
            RascunhoCurriculoAdaptado(
                nome_completo="Ana Souza",
                email="ana@ex.com",
                linkedin="",
                secoes=(),
                experiencias=(_experiencia(empresa=""),),
            )

    def test_rascunho_apenas_com_experiencias_e_valido(self):
        rascunho = RascunhoCurriculoAdaptado(
            nome_completo="Ana Souza",
            email="ana@ex.com",
            linkedin="",
            secoes=(),
            experiencias=(_experiencia(),),
        )

        assert rascunho.experiencias == (_experiencia(),)

    def test_para_curriculo_preserva_cabecalho_e_secoes_de_texto(self):
        rascunho = RascunhoCurriculoAdaptado(
            nome_completo="Ana Souza",
            email="ana@ex.com",
            linkedin="linkedin.com/in/ana",
            secoes=(_secao_perfil(),),
        )

        curriculo = rascunho.para_curriculo()

        assert curriculo.nome_completo == "Ana Souza"
        assert curriculo.email == "ana@ex.com"
        assert curriculo.linkedin == "linkedin.com/in/ana"
        assert curriculo.secoes == (_secao_perfil(),)

    def test_para_curriculo_monta_secao_de_experiencias_no_formato_do_pdf(self):
        rascunho = RascunhoCurriculoAdaptado(
            nome_completo="Ana Souza",
            email="ana@ex.com",
            linkedin="",
            secoes=(_secao_perfil(),),
            experiencias=(
                _experiencia(),
                _experiencia(
                    cargo="Dev", empresa="TechCorp", periodo="", descricao="  Criei testes.  "
                ),
            ),
            titulo_experiencias="Professional Experience",
        )

        secao = rascunho.para_curriculo().obter_secao(TipoSecao.EXPERIENCIAS)

        assert secao == SecaoCurriculo(
            TipoSecao.EXPERIENCIAS,
            "Professional Experience",
            "Engenheiro de Software — Starian (2022 - Atual)\nDesenvolvi APIs em Java."
            "\n\nDev — TechCorp\nCriei testes.",
        )

    def test_para_curriculo_sem_experiencias_estruturadas_nao_cria_secao(self):
        rascunho = RascunhoCurriculoAdaptado(
            nome_completo="Ana Souza",
            email="ana@ex.com",
            linkedin="",
            secoes=(_secao_perfil(),),
            experiencias=(),
        )

        curriculo = rascunho.para_curriculo()

        assert curriculo.obter_secao(TipoSecao.EXPERIENCIAS) is None

    def test_revisado_descarta_secoes_em_branco(self):
        rascunho = RascunhoCurriculoAdaptado.revisado(
            nome_completo="Ana Souza",
            email="ana@ex.com",
            linkedin="",
            secoes=(
                (TipoSecao.PERFIL, "Perfil", "Engenheiro backend."),
                (TipoSecao.FORMACAO, "Formação", "   "),
            ),
            experiencias=None,
        )

        assert rascunho.secoes == (_secao_perfil(),)
        assert rascunho.experiencias is None

    def test_revisado_descarta_experiencias_totalmente_em_branco(self):
        rascunho = RascunhoCurriculoAdaptado.revisado(
            nome_completo="Ana Souza",
            email="ana@ex.com",
            linkedin="",
            secoes=(),
            experiencias=(
                _experiencia(),
                _experiencia(cargo=" ", empresa="", periodo="", descricao=" "),
            ),
        )

        assert rascunho.experiencias == (_experiencia(),)

    def test_revisado_preserva_titulo_das_experiencias(self):
        rascunho = RascunhoCurriculoAdaptado.revisado(
            nome_completo="Ana Souza",
            email="ana@ex.com",
            linkedin="",
            secoes=(),
            experiencias=(_experiencia(),),
            titulo_experiencias="Experience",
        )

        assert rascunho.titulo_experiencias == "Experience"
