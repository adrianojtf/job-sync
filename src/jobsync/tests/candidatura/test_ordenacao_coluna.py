"""Testes da regra de reordenação de uma coluna do Kanban."""

import pytest

from jobsync.candidatura.domain.ordenacao_coluna import reposicionar


class TestReposicionar:
    @pytest.mark.parametrize(
        ("ids", "movido", "posicao", "esperado"),
        [
            (("a", "b", "c"), "x", 0, ("x", "a", "b", "c")),
            (("a", "b", "c"), "x", 1, ("a", "x", "b", "c")),
            (("a", "b", "c"), "x", 3, ("a", "b", "c", "x")),
            ((), "x", 0, ("x",)),
        ],
    )
    def test_insere_cartao_vindo_de_outra_coluna(self, ids, movido, posicao, esperado):
        assert reposicionar(ids, movido, posicao) == esperado

    def test_posicao_omitida_coloca_no_topo(self):
        assert reposicionar(("a", "b"), "x", None) == ("x", "a", "b")

    def test_posicao_acima_do_tamanho_coloca_no_fim(self):
        assert reposicionar(("a", "b"), "x", 99) == ("a", "b", "x")

    @pytest.mark.parametrize(
        ("movido", "posicao", "esperado"),
        [
            ("a", 2, ("b", "c", "a")),
            ("c", 0, ("c", "a", "b")),
            ("b", 1, ("a", "b", "c")),
            ("a", None, ("a", "b", "c")),
        ],
    )
    def test_reordena_cartao_que_ja_esta_na_coluna(self, movido, posicao, esperado):
        assert reposicionar(("a", "b", "c"), movido, posicao) == esperado

    def test_nao_altera_a_tupla_original(self):
        original = ("a", "b")

        reposicionar(original, "x", 0)

        assert original == ("a", "b")

    def test_posicao_negativa_levanta_erro(self):
        with pytest.raises(ValueError):
            reposicionar(("a",), "x", -1)
