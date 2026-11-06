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
        texto = _experiencia().para_texto("Context")

        assert texto == (
            "Software Engineer — SIPPulse (2022 - Atual)\n"
            "- Developed a VoIP billing system.\n"
            "- Accelerated processing by 95%.\n"
            "Context: Worked on the communications platform."
        )

    def test_para_texto_sem_contexto_nao_deixa_rotulo_solto(self):
        texto = _experiencia(contexto="  ").para_texto("Context")

        assert texto == (
            "Software Engineer — SIPPulse (2022 - Atual)\n"
            "- Developed a VoIP billing system.\n"
            "- Accelerated processing by 95%."
        )

    def test_para_texto_sem_conquistas_traz_cabecalho_e_contexto(self):
        texto = _experiencia(conquistas=()).para_texto("Contexto")

        assert texto == (
            "Software Engineer — SIPPulse (2022 - Atual)\n"
            "Contexto: Worked on the communications platform."
        )

    def test_para_texto_sem_conquistas_e_sem_contexto_traz_so_o_cabecalho(self):
        texto = _experiencia(conquistas=(), contexto="").para_texto("Contexto")

        assert texto == "Software Engineer — SIPPulse (2022 - Atual)"

    def test_para_texto_sem_periodo_omite_os_parenteses(self):
        texto = _experiencia(periodo=" ", conquistas=(), contexto="").para_texto("Context")

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


class TestExperienciaAdaptadaDeDescricao:
    def test_cada_linha_da_descricao_vira_uma_conquista_sem_marcadores(self):
        experiencia = ExperienciaAdaptada.de_descricao(
            cargo="Dev",
            empresa="TechCorp",
            periodo="2024",
            descricao="- Criei APIs.\n• Reduzi custos.\n\n  Mantive serviços.  ",
        )

        assert experiencia.conquistas == ("Criei APIs.", "Reduzi custos.", "Mantive serviços.")
        assert experiencia.contexto == ""

    def test_descricao_vazia_resulta_sem_conquistas(self):
        experiencia = ExperienciaAdaptada.de_descricao("Dev", "TechCorp", "", "  ")

        assert experiencia.conquistas == ()


class TestRotulosExperiencia:
    @pytest.mark.parametrize(("idioma", "rotulo"), [("pt", "Contexto"), ("en", "Context")])
    def test_rotulo_do_contexto_segue_o_idioma_alvo(self, idioma, rotulo):
        assert rotulo_contexto(idioma) == rotulo

    def test_idioma_nao_suportado_gera_erro(self):
        with pytest.raises(ValueError, match="idioma"):
            rotulo_contexto("fr")

    def test_rotulos_reconhecidos_cobrem_os_dois_idiomas_em_minusculas(self):
        assert ROTULOS_CONTEXTO_RECONHECIDOS == frozenset({"contexto", "context"})
