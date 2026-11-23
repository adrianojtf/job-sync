"""Testes do agregado CurriculoAdaptado."""
import pytest

from jobsync.curriculo import RascunhoCurriculoAdaptado, SecaoCurriculo, TipoSecao
from jobsync.curriculo_adaptado.domain.curriculo_adaptado import CurriculoAdaptado
from jobsync.tests.curriculo_adaptado.exemplos import (
    AGORA,
    DEPOIS,
    analise_vaga,
    curriculo_adaptado,
    rascunho,
)


class TestCurriculoAdaptado:
    @pytest.mark.parametrize(
        "campo, mensagem",
        [
            ("id", "id"),
            ("perfil_identificador", "perfil"),
            ("nome_referencia", "nome de referência"),
            ("cargo_alvo", "cargo"),
            ("empresa_alvo", "empresa"),
            ("idioma_alvo", "idioma"),
            ("descricao_vaga", "descrição da vaga"),
        ],
    )
    def test_campo_obrigatorio_em_branco_gera_erro(self, campo, mensagem):
        with pytest.raises(ValueError, match=mensagem):
            curriculo_adaptado(**{campo: "  "})

    def test_novo_gera_id_define_as_datas_e_nao_vincula_curriculo_salvo(self):
        curriculo = CurriculoAdaptado.novo(
            perfil_identificador="ana",
            nome_referencia="Ana_Souza_Dev_TechCorp.pdf",
            cargo_alvo="Engenheira de Software",
            empresa_alvo="TechCorp",
            idioma_alvo="pt",
            descricao_vaga="Vaga Java com code review.",
            analise_vaga=analise_vaga(),
            rascunho=rascunho(),
            agora=AGORA,
        )

        assert curriculo.id
        assert curriculo.criado_em == AGORA
        assert curriculo.atualizado_em == AGORA
        assert curriculo.curriculo_salvo_id is None

    def test_novo_gera_ids_diferentes(self):
        dados = dict(
            perfil_identificador="ana",
            nome_referencia="a.pdf",
            cargo_alvo="Dev",
            empresa_alvo="X",
            idioma_alvo="pt",
            descricao_vaga="Vaga",
            analise_vaga=analise_vaga(),
            rascunho=rascunho(),
            agora=AGORA,
        )

        assert CurriculoAdaptado.novo(**dados).id != CurriculoAdaptado.novo(**dados).id

    def test_com_rascunho_revisado_troca_o_conteudo_e_atualiza_so_a_data_de_atualizacao(self):
        original = curriculo_adaptado()
        revisado = rascunho().__class__.revisado(
            nome_completo="Ana Souza",
            email="ana@ex.com",
            linkedin="",
            secoes=(),
            experiencias=None,
            competencias=(("Linguagens", ("Go",)),),
        )

        novo = original.com_rascunho_revisado(revisado, DEPOIS)

        assert novo.rascunho == revisado
        assert novo.atualizado_em == DEPOIS
        assert novo.criado_em == AGORA
        assert novo.id == original.id
        assert original.atualizado_em == AGORA

    def test_com_curriculo_salvo_guarda_o_vinculo_sem_alterar_o_resto(self):
        original = curriculo_adaptado()

        vinculado = original.com_curriculo_salvo("salvo-9")

        assert vinculado.curriculo_salvo_id == "salvo-9"
        assert vinculado.rascunho == original.rascunho
        assert original.curriculo_salvo_id is None


class TestCurriculoAdaptadoComoBase:
    def test_como_curriculo_base_devolve_o_conteudo_salvo_no_idioma_do_currículo(self):
        base = curriculo_adaptado().como_curriculo_base()

        assert base == rascunho().para_curriculo("pt")

    def test_o_curriculo_base_traz_as_competencias_em_texto_e_as_experiencias(self):
        base = curriculo_adaptado().como_curriculo_base()

        tecnologias = base.obter_secao(TipoSecao.TECNOLOGIAS)
        assert tecnologias.conteudo == "Linguagens: Java, Python\nBancos de Dados: SQL"
        assert base.obter_secao(TipoSecao.EXPERIENCIAS) is not None

    def test_experiencias_para_adaptacao_devolve_as_estruturadas_como_texto_de_conquistas_e_contexto(self):
        experiencias = curriculo_adaptado().experiencias_para_adaptacao()

        assert [(e.cargo, e.empresa, e.periodo) for e in experiencias] == [
            ("Dev", "TechCorp", "2024 - Atual")
        ]
        assert experiencias[0].descricao == (
            "- Criei APIs.\n- Reduzi custos em 30%.\nPlataforma de pagamentos."
        )

    def test_experiencias_para_adaptacao_e_none_quando_as_experiencias_vem_em_texto(self):
        de_pdf = RascunhoCurriculoAdaptado(
            nome_completo="Ana Souza",
            email="",
            linkedin="",
            secoes=(SecaoCurriculo(TipoSecao.EXPERIENCIAS, "Experiências", "Dev — TechCorp"),),
        )

        assert curriculo_adaptado(rascunho=de_pdf).experiencias_para_adaptacao() is None

    def test_o_curriculo_de_origem_nao_muda_ao_ser_usado_como_base(self):
        original = curriculo_adaptado()

        original.como_curriculo_base()
        original.experiencias_para_adaptacao()

        assert original == curriculo_adaptado()
