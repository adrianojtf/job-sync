"""Testes da regra de similaridade textual entre conquistas."""

import pytest

from jobsync.perfil_estruturado.domain.conquistas_parecidas import sao_parecidas


class TestSaoParecidas:
    def test_textos_iguais_apos_normalizacao_sao_parecidos(self):
        assert sao_parecidas("Reduzi o tempo de deploy.", "reduzi o TEMPO de deploy")

    def test_acento_e_pontuacao_nao_diferenciam(self):
        assert sao_parecidas("Implantei a integração, com testes.", "implantei a integracao com testes")

    def test_parafrase_com_alta_sobreposicao_e_parecida(self):
        assert sao_parecidas(
            "Reduzi o tempo de deploy em 40% com pipeline automatizado.",
            "Reduzi o tempo de deploy com o pipeline automatizado.",
        )

    @pytest.mark.parametrize(
        "texto_a, texto_b",
        [
            ("Liderei a migração do banco de dados.", "Construí uma API de pagamentos."),
            ("Reduzi o tempo de deploy.", "Reduzi o custo de infraestrutura na nuvem."),
        ],
    )
    def test_textos_distintos_nao_sao_parecidos(self, texto_a, texto_b):
        assert not sao_parecidas(texto_a, texto_b)

    def test_textos_sem_palavras_relevantes_e_diferentes_nao_sao_parecidos(self):
        assert not sao_parecidas("de a o", "em e u")
