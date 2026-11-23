"""Testes do agregado CurriculoAdaptado."""
import pytest

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
