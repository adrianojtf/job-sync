"""Testes do Value Object ExperienciaAdaptada e dos rótulos do contexto."""
import pytest

from jobsync.curriculo import ExperienciaAdaptada, ExperienciaParaAvaliacao
from jobsync.curriculo.domain.rotulos_experiencia import (
    ROTULOS_CONTEXTO_RECONHECIDOS,
    rotulo_contexto,
)


def _experiencia(**sobrescritas) -> ExperienciaAdaptada:
    valores = {
        "cargo": "Software Engineer",
        "empresa": "SIPPulse",
        "periodo": "2022 - Atual",
        "conquistas": ("Developed a VoIP billing system.", "Accelerated processing by 95%."),
        "contexto": "Worked on the communications platform.",
    }
    valores.update(sobrescritas)
    return ExperienciaAdaptada(**valores)


class TestExperienciaAdaptada:
    @pytest.mark.parametrize("campo", ["cargo", "empresa"])
    def test_cargo_e_empresa_sao_obrigatorios(self, campo):
        with pytest.raises(ValueError, match=campo):
            _experiencia(**{campo: "  "})

    def test_conquista_em_branco_gera_erro(self):
        with pytest.raises(ValueError, match="conquista"):
            _experiencia(conquistas=("Entrega A.", "  "))

    def test_conquistas_e_contexto_sao_opcionais(self):
        experiencia = _experiencia(conquistas=(), contexto="")

        assert experiencia.conquistas == ()
        assert experiencia.contexto == ""

    def test_para_texto_monta_cabecalho_bullets_e_contexto_com_rotulo(self):
        texto = _experiencia().para_texto("en")

        assert texto == (
            "Software Engineer — SIPPulse (2022 - Atual)\n"
            "- Developed a VoIP billing system.\n"
            "- Accelerated processing by 95%.\n"
            "Context: Worked on the communications platform."
        )

    def test_para_texto_sem_contexto_nao_deixa_rotulo_solto(self):
        texto = _experiencia(contexto="  ").para_texto("en")

        assert texto == (
            "Software Engineer — SIPPulse (2022 - Atual)\n"
            "- Developed a VoIP billing system.\n"
            "- Accelerated processing by 95%."
        )

    def test_para_texto_sem_conquistas_traz_cabecalho_e_contexto(self):
        texto = _experiencia(conquistas=()).para_texto("pt")

        assert texto == (
            "Software Engineer — SIPPulse (2022 - Atual)\n"
            "Contexto: Worked on the communications platform."
        )

    def test_para_texto_sem_conquistas_e_sem_contexto_traz_so_o_cabecalho(self):
        texto = _experiencia(conquistas=(), contexto="").para_texto("pt")

        assert texto == "Software Engineer — SIPPulse (2022 - Atual)"

    def test_para_texto_sem_periodo_omite_os_parenteses(self):
        texto = _experiencia(periodo=" ", conquistas=(), contexto="").para_texto("en")

        assert texto == "Software Engineer — SIPPulse"

    def test_para_avaliacao_compoe_bullets_e_contexto_sem_cabecalho_nem_rotulo(self):
        avaliacao = _experiencia().para_avaliacao()

        assert avaliacao == ExperienciaParaAvaliacao(
            cargo="Software Engineer",
            empresa="SIPPulse",
            periodo="2022 - Atual",
            descricao=(
                "- Developed a VoIP billing system.\n"
                "- Accelerated processing by 95%.\n"
                "Worked on the communications platform."
            ),
        )


class TestExperienciaAdaptadaTemConteudo:
    def test_com_conquistas_ou_contexto_tem_conteudo(self):
        assert _experiencia(conquistas=("Criei APIs.",), contexto="").tem_conteudo
        assert _experiencia(conquistas=(), contexto="Empresa de pagamentos.").tem_conteudo

    def test_sem_conquistas_e_com_contexto_em_branco_nao_tem_conteudo(self):
        assert not _experiencia(conquistas=(), contexto="  ").tem_conteudo


class TestExperienciaAdaptadaRevisada:
    def test_apara_os_campos_e_descarta_conquistas_em_branco(self):
        experiencia = ExperienciaAdaptada.revisada(
            cargo=" Dev ",
            empresa=" TechCorp",
            periodo=" 2024 ",
            conquistas=(" Entrega A. ", "", "   ", "Entrega B."),
            contexto="  Contexto da empresa.  ",
        )

        assert experiencia == ExperienciaAdaptada(
            cargo="Dev",
            empresa="TechCorp",
            periodo="2024",
            conquistas=("Entrega A.", "Entrega B."),
            contexto="Contexto da empresa.",
        )

    def test_experiencia_totalmente_em_branco_devolve_none(self):
        experiencia = ExperienciaAdaptada.revisada(
            cargo=" ", empresa="", periodo="", conquistas=("", " "), contexto=" "
        )

        assert experiencia is None

    def test_experiencia_parcialmente_preenchida_sem_empresa_gera_erro(self):
        with pytest.raises(ValueError, match="empresa"):
            ExperienciaAdaptada.revisada(
                cargo="Dev", empresa="", periodo="", conquistas=("Entrega A.",), contexto=""
            )


class TestExperienciaAdaptadaComoDescricao:
    def test_conquistas_por_linha_sem_marcadores_seguidas_do_contexto(self):
        descricao = _experiencia().como_descricao()

        assert descricao == (
            "Developed a VoIP billing system.\n"
            "Accelerated processing by 95%.\n"
            "Worked on the communications platform."
        )

    def test_sem_contexto_traz_so_as_conquistas(self):
        assert _experiencia(contexto="").como_descricao() == (
            "Developed a VoIP billing system.\nAccelerated processing by 95%."
        )

    def test_sem_conquistas_e_sem_contexto_devolve_texto_vazio(self):
        assert _experiencia(conquistas=(), contexto="").como_descricao() == ""


class TestRotulosExperiencia:
    @pytest.mark.parametrize(("idioma", "rotulo"), [("pt", "Contexto"), ("en", "Context")])
    def test_rotulo_do_contexto_segue_o_idioma_alvo(self, idioma, rotulo):
        assert rotulo_contexto(idioma) == rotulo

    def test_idioma_nao_suportado_gera_erro(self):
        with pytest.raises(ValueError, match="idioma"):
            rotulo_contexto("fr")

    def test_rotulos_reconhecidos_cobrem_os_dois_idiomas_em_minusculas(self):
        assert ROTULOS_CONTEXTO_RECONHECIDOS == frozenset({"contexto", "context"})


def _estruturada(**sobrescritas) -> ExperienciaAdaptada:
    valores = {
        "responsabilidades": ("Design and deliver features.", "Coordinate with Product and QA."),
        "skills": ("Java", "PostgreSQL"),
    }
    valores.update(sobrescritas)
    return _experiencia(**valores)


class TestExperienciaAdaptadaComQuatroBlocos:
    def test_responsabilidades_e_skills_sao_opcionais(self):
        experiencia = _experiencia()

        assert experiencia.responsabilidades == ()
        assert experiencia.skills == ()

    @pytest.mark.parametrize("campo", ["responsabilidades", "skills"])
    def test_item_em_branco_gera_erro(self, campo):
        with pytest.raises(ValueError, match=campo[:5]):
            _estruturada(**{campo: ("Item.", "  ")})

    def test_so_responsabilidades_ou_so_skills_ja_e_conteudo(self):
        assert _experiencia(conquistas=(), contexto="", responsabilidades=("Projetar.",)).tem_conteudo
        assert _experiencia(conquistas=(), contexto="", skills=("Java",)).tem_conteudo

    def test_para_texto_em_ingles_traz_os_quatro_blocos_com_rotulos(self):
        texto = _estruturada().para_texto("en")

        assert texto == (
            "Software Engineer — SIPPulse (2022 - Atual)\n"
            "Context: Worked on the communications platform.\n"
            "Key Responsibilities:\n"
            "- Design and deliver features.\n"
            "- Coordinate with Product and QA.\n"
            "Key Achievements:\n"
            "- Developed a VoIP billing system.\n"
            "- Accelerated processing by 95%.\n"
            "Technologies: Java | PostgreSQL"
        )

    def test_para_texto_em_portugues_traduz_os_rotulos(self):
        texto = _estruturada().para_texto("pt")

        assert "Contexto: Worked on" in texto
        assert "Principais responsabilidades:" in texto
        assert "Principais realizações:" in texto
        assert "Tecnologias: Java | PostgreSQL" in texto

    def test_para_texto_omite_o_bloco_vazio_sem_rotulo_solto(self):
        texto = _estruturada(responsabilidades=(), conquistas=(), contexto="").para_texto("en")

        assert texto == "Software Engineer — SIPPulse (2022 - Atual)\nTechnologies: Java | PostgreSQL"

    def test_para_texto_com_so_skills_e_conquistas_ainda_usa_os_cabecalhos(self):
        texto = _estruturada(responsabilidades=()).para_texto("en")

        assert "Key Achievements:" in texto
        assert "Key Responsibilities:" not in texto

    def test_para_texto_idioma_invalido_gera_erro(self):
        with pytest.raises(ValueError, match="idioma"):
            _estruturada().para_texto("fr")

    def test_para_avaliacao_considera_os_quatro_blocos(self):
        avaliacao = _estruturada().para_avaliacao()

        assert avaliacao.descricao == (
            "- Design and deliver features.\n"
            "- Coordinate with Product and QA.\n"
            "- Developed a VoIP billing system.\n"
            "- Accelerated processing by 95%.\n"
            "Worked on the communications platform.\n"
            "Java, PostgreSQL"
        )

    def test_como_descricao_considera_os_quatro_blocos(self):
        assert _estruturada().como_descricao() == (
            "Design and deliver features.\n"
            "Coordinate with Product and QA.\n"
            "Developed a VoIP billing system.\n"
            "Accelerated processing by 95%.\n"
            "Worked on the communications platform.\n"
            "Java, PostgreSQL"
        )

    def test_revisada_apara_e_descarta_itens_em_branco_dos_novos_blocos(self):
        experiencia = ExperienciaAdaptada.revisada(
            cargo="Dev", empresa="TechCorp", periodo="2024", conquistas=("A.",), contexto="",
            responsabilidades=(" Projetar ", ""), skills=(" Java ", "  "),
        )

        assert experiencia.responsabilidades == ("Projetar",)
        assert experiencia.skills == ("Java",)

    def test_revisada_com_so_um_bloco_novo_preenchido_nao_e_tratada_como_em_branco(self):
        with pytest.raises(ValueError, match="cargo"):
            ExperienciaAdaptada.revisada(
                cargo="", empresa="", periodo="", conquistas=(), contexto="", skills=("Java",)
            )
