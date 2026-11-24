"""Testes da serialização do conteúdo do currículo adaptado em JSON."""
import json

from jobsync.curriculo import ExperienciaAdaptada, RascunhoCurriculoAdaptado, SecaoCurriculo, TipoSecao
from jobsync.curriculo_adaptado.adapters.serializador_conteudo import (
    VERSAO_DO_FORMATO,
    analise_de_json,
    analise_para_json,
    rascunho_de_json,
    rascunho_para_json,
)
from jobsync.tests.curriculo_adaptado.exemplos import analise_vaga, rascunho


class TestRascunhoParaJson:
    def test_ida_e_volta_preserva_o_rascunho_completo(self):
        original = rascunho()

        assert rascunho_de_json(rascunho_para_json(original)) == original

    def test_o_json_e_serializavel_e_traz_a_versao_do_formato(self):
        conteudo = rascunho_para_json(rascunho())

        assert json.loads(json.dumps(conteudo))["versao"] == VERSAO_DO_FORMATO

    def test_rascunho_de_pdf_sem_experiencias_estruturadas_nem_competencias_volta_igual(self):
        original = RascunhoCurriculoAdaptado(
            nome_completo="Ana Souza",
            email="",
            linkedin="",
            secoes=(SecaoCurriculo(TipoSecao.EXPERIENCIAS, "Experiências", "Dev — TechCorp"),),
        )

        recuperado = rascunho_de_json(rascunho_para_json(original))

        assert recuperado == original
        assert recuperado.experiencias is None
        assert recuperado.competencias is None

    def test_competencias_vazias_e_nulas_sao_diferentes_apos_a_volta(self):
        base = dict(
            nome_completo="Ana Souza",
            email="",
            linkedin="",
            secoes=(SecaoCurriculo(TipoSecao.PERFIL, "Perfil", "Texto."),),
        )
        vazia = RascunhoCurriculoAdaptado(**base, competencias=())
        nula = RascunhoCurriculoAdaptado(**base)

        assert rascunho_de_json(rascunho_para_json(vazia)).competencias == ()
        assert rascunho_de_json(rascunho_para_json(nula)).competencias is None

    def test_formato_de_versao_desconhecida_gera_erro(self):
        conteudo = rascunho_para_json(rascunho())
        conteudo["versao"] = 999

        try:
            rascunho_de_json(conteudo)
        except ValueError as erro:
            assert "versão" in str(erro)
        else:
            raise AssertionError("era esperado ValueError")


class TestRascunhoComQuatroBlocos:
    def _com_blocos(self) -> RascunhoCurriculoAdaptado:
        return RascunhoCurriculoAdaptado(
            nome_completo="Ana Souza",
            email="",
            linkedin="",
            secoes=(),
            experiencias=(
                ExperienciaAdaptada(
                    cargo="Dev",
                    empresa="Starian",
                    periodo="2024",
                    conquistas=("Atendi 1.000 usuários.",),
                    contexto="ERP financeiro.",
                    responsabilidades=("Projetar telas.",),
                    skills=("Java", "SQL"),
                ),
            ),
        )

    def test_a_versao_atual_do_formato_e_a_2(self):
        assert VERSAO_DO_FORMATO == 2

    def test_ida_e_volta_preserva_responsabilidades_e_skills(self):
        original = self._com_blocos()

        assert rascunho_de_json(rascunho_para_json(original)) == original

    def test_json_da_versao_1_e_lido_com_os_blocos_novos_vazios(self):
        conteudo = rascunho_para_json(self._com_blocos())
        conteudo["versao"] = 1
        for experiencia in conteudo["experiencias"]:
            del experiencia["responsabilidades"]
            del experiencia["skills"]

        recuperado = rascunho_de_json(conteudo)

        experiencia = recuperado.experiencias[0]
        assert experiencia.conquistas == ("Atendi 1.000 usuários.",)
        assert (experiencia.responsabilidades, experiencia.skills) == ((), ())


class TestAnaliseParaJson:
    def test_ida_e_volta_preserva_a_analise_da_vaga(self):
        original = analise_vaga()

        assert analise_de_json(analise_para_json(original)) == original

    def test_o_json_e_serializavel(self):
        assert json.dumps(analise_para_json(analise_vaga()))
