"""Testes do agregado RascunhoCurriculoAdaptado."""
import pytest

from jobsync.curriculo import (
    ExperienciaAdaptada,
    RascunhoCurriculoAdaptado,
    SecaoCurriculo,
    TipoSecao,
)


def _experiencia(
    cargo: str = "Engenheiro de Software",
    empresa: str = "Starian",
    periodo: str = "2022 - Atual",
    conquistas: tuple[str, ...] = ("Desenvolvi APIs em Java.",),
    contexto: str = "",
) -> ExperienciaAdaptada:
    return ExperienciaAdaptada(
        cargo=cargo, empresa=empresa, periodo=periodo, conquistas=conquistas, contexto=contexto
    )


def _secao_perfil() -> SecaoCurriculo:
    return SecaoCurriculo(TipoSecao.PERFIL, "Perfil", "Engenheiro backend.")


def _rascunho(**sobrescritas) -> RascunhoCurriculoAdaptado:
    valores = {
        "nome_completo": "Ana Souza",
        "email": "ana@ex.com",
        "linkedin": "",
        "secoes": (_secao_perfil(),),
    }
    valores.update(sobrescritas)
    return RascunhoCurriculoAdaptado(**valores)


class TestRascunhoCurriculoAdaptado:
    def test_nome_completo_vazio_gera_erro(self):
        with pytest.raises(ValueError, match="nome completo"):
            _rascunho(nome_completo="  ")

    def test_rascunho_sem_secoes_e_sem_experiencias_gera_erro(self):
        with pytest.raises(ValueError, match="ao menos uma seção"):
            _rascunho(secoes=(), experiencias=())

    def test_secao_de_experiencias_com_experiencias_estruturadas_gera_erro(self):
        with pytest.raises(ValueError, match="experiências"):
            _rascunho(
                secoes=(SecaoCurriculo(TipoSecao.EXPERIENCIAS, "Experiências", "texto"),),
                experiencias=(_experiencia(),),
            )

    def test_rascunho_apenas_com_experiencias_e_valido(self):
        rascunho = _rascunho(secoes=(), experiencias=(_experiencia(),))

        assert rascunho.experiencias == (_experiencia(),)

    def test_para_curriculo_preserva_cabecalho_e_secoes_de_texto(self):
        rascunho = _rascunho(linkedin="linkedin.com/in/ana")

        curriculo = rascunho.para_curriculo("pt")

        assert curriculo.nome_completo == "Ana Souza"
        assert curriculo.email == "ana@ex.com"
        assert curriculo.linkedin == "linkedin.com/in/ana"
        assert curriculo.secoes == (_secao_perfil(),)

    def test_para_curriculo_monta_secao_de_experiencias_com_bullets_e_contexto(self):
        rascunho = _rascunho(
            experiencias=(
                _experiencia(
                    conquistas=("Desenvolvi APIs em Java.", "Reduzi o tempo em 30%."),
                    contexto="Plataforma financeira com milhares de usuários.",
                ),
                _experiencia(cargo="Dev", empresa="TechCorp", periodo="", conquistas=("Criei testes.",)),
            ),
            titulo_experiencias="Professional Experience",
        )

        secao = rascunho.para_curriculo("en").obter_secao(TipoSecao.EXPERIENCIAS)

        assert secao == SecaoCurriculo(
            TipoSecao.EXPERIENCIAS,
            "Professional Experience",
            "Engenheiro de Software — Starian (2022 - Atual)\n"
            "- Desenvolvi APIs em Java.\n"
            "- Reduzi o tempo em 30%.\n"
            "Context: Plataforma financeira com milhares de usuários."
            "\n\n"
            "Dev — TechCorp\n"
            "- Criei testes.",
        )

    def test_para_curriculo_usa_o_rotulo_do_idioma_alvo(self):
        rascunho = _rascunho(experiencias=(_experiencia(contexto="Empresa de telecom."),))

        secao = rascunho.para_curriculo("pt").obter_secao(TipoSecao.EXPERIENCIAS)

        assert "\nContexto: Empresa de telecom." in secao.conteudo

    def test_para_curriculo_com_idioma_nao_suportado_gera_erro(self):
        with pytest.raises(ValueError, match="idioma"):
            _rascunho().para_curriculo("fr")

    def test_para_curriculo_sem_experiencias_estruturadas_nao_cria_secao(self):
        rascunho = _rascunho(experiencias=())

        curriculo = rascunho.para_curriculo("pt")

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

    def test_revisado_monta_experiencias_e_descarta_as_totalmente_em_branco(self):
        rascunho = RascunhoCurriculoAdaptado.revisado(
            nome_completo="Ana Souza",
            email="ana@ex.com",
            linkedin="",
            secoes=(),
            experiencias=(
                (" Dev ", "TechCorp", "2024", ("  Entrega A. ", ""), " Contexto. "),
                (" ", "", "", ("", " "), " "),
            ),
        )

        assert rascunho.experiencias == (
            ExperienciaAdaptada(
                cargo="Dev",
                empresa="TechCorp",
                periodo="2024",
                conquistas=("Entrega A.",),
                contexto="Contexto.",
            ),
        )

    def test_revisado_com_experiencia_sem_empresa_gera_erro(self):
        with pytest.raises(ValueError, match="empresa"):
            RascunhoCurriculoAdaptado.revisado(
                nome_completo="Ana Souza",
                email="",
                linkedin="",
                secoes=(),
                experiencias=(("Dev", "", "", ("Entrega A.",), ""),),
            )

    def test_revisado_preserva_titulo_das_experiencias(self):
        rascunho = RascunhoCurriculoAdaptado.revisado(
            nome_completo="Ana Souza",
            email="ana@ex.com",
            linkedin="",
            secoes=(),
            experiencias=(("Dev", "TechCorp", "", ("Entrega A.",), ""),),
            titulo_experiencias="Experience",
        )

        assert rascunho.titulo_experiencias == "Experience"
