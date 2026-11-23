"""Testes das regras de domínio das lacunas da vaga (JOB-0043)."""
import pytest

from jobsync.curriculo import ExperienciaParaAvaliacao
from jobsync.curriculo.domain.lacuna_da_vaga import (
    LIMITE_DE_LACUNAS,
    HistoricoDoCandidato,
    LacunaDaVaga,
    principais,
)


def _lacuna(tema: str, pergunta: str = "Você já fez isso?") -> LacunaDaVaga:
    return LacunaDaVaga(tema=tema, pergunta=pergunta)


class TestLacunaDaVaga:
    def test_aparar_tema_e_pergunta(self):
        lacuna = LacunaDaVaga(tema="  Atuação com clientes ", pergunta=" Você já atuou com clientes? ")

        assert lacuna.tema == "Atuação com clientes"
        assert lacuna.pergunta == "Você já atuou com clientes?"

    @pytest.mark.parametrize("tema, pergunta", [("", "Você já fez?"), ("  ", "Você já fez?"), ("Tema", " ")])
    def test_tema_ou_pergunta_vazios_levantam_erro(self, tema, pergunta):
        with pytest.raises(ValueError):
            LacunaDaVaga(tema=tema, pergunta=pergunta)


class TestPrincipais:
    def test_limite_padrao_e_5(self):
        assert LIMITE_DE_LACUNAS == 5

    def test_corta_no_limite_mantendo_a_ordem(self):
        lacunas = tuple(_lacuna(f"Tema {n}") for n in range(8))

        resultado = principais(lacunas)

        assert resultado == lacunas[:5]

    def test_remove_tema_repetido_ignorando_caixa_e_acento(self):
        lacunas = (_lacuna("Atuação com clientes"), _lacuna("atuacao com CLIENTES", "Outra pergunta?"), _lacuna("MVP"))

        resultado = principais(lacunas)

        assert [lacuna.tema for lacuna in resultado] == ["Atuação com clientes", "MVP"]

    def test_duplicata_nao_ocupa_vaga_do_limite(self):
        lacunas = (_lacuna("A"), _lacuna("a"), _lacuna("B"), _lacuna("C"))

        resultado = principais(lacunas, limite=3)

        assert [lacuna.tema for lacuna in resultado] == ["A", "B", "C"]

    def test_sem_lacunas_devolve_tupla_vazia(self):
        assert principais(()) == ()


class TestHistoricoDoCandidato:
    def test_sem_experiencias_nao_tem_o_que_comparar(self):
        assert HistoricoDoCandidato(resumo="Backend.", experiencias=(), tecnologias=("Java",)).sem_experiencias()

    def test_com_experiencias_tem_o_que_comparar(self):
        experiencia = ExperienciaParaAvaliacao(descricao="APIs.", cargo="Dev", empresa="TechCorp", periodo="2020")

        historico = HistoricoDoCandidato(resumo="", experiencias=(experiencia,), tecnologias=())

        assert not historico.sem_experiencias()
