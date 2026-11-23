"""Testes da serialização do conteúdo do currículo adaptado em JSON."""
import json

from jobsync.curriculo import RascunhoCurriculoAdaptado, SecaoCurriculo, TipoSecao
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


class TestAnaliseParaJson:
    def test_ida_e_volta_preserva_a_analise_da_vaga(self):
        original = analise_vaga()

        assert analise_de_json(analise_para_json(original)) == original

    def test_o_json_e_serializavel(self):
        assert json.dumps(analise_para_json(analise_vaga()))
