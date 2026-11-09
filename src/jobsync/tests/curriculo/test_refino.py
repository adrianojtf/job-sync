"""Testes dos Value Objects de refino das sugestões de IA."""
import pytest

from jobsync.curriculo import FocoRefino, PedidoRefino, SugestaoRefinada


class TestPedidoRefino:
    def test_padrao_e_a_primeira_tentativa_sem_sugestoes_anteriores(self):
        refino = PedidoRefino()

        assert refino.tentativa == 1
        assert refino.sugestoes_anteriores == ()

    def test_com_vaga_os_focos_seguem_um_rodizio_de_quatro(self):
        focos = [PedidoRefino(tentativa=tentativa).foco(com_vaga=True) for tentativa in range(1, 6)]

        assert focos == [
            FocoRefino.ADERENCIA_VAGA,
            FocoRefino.IMPACTO,
            FocoRefino.PALAVRAS_CHAVE,
            FocoRefino.CLAREZA_CONCISAO,
            FocoRefino.ADERENCIA_VAGA,
        ]

    def test_sem_vaga_os_focos_seguem_um_rodizio_de_tres(self):
        focos = [PedidoRefino(tentativa=tentativa).foco(com_vaga=False) for tentativa in range(1, 5)]

        assert focos == [
            FocoRefino.IMPACTO,
            FocoRefino.CLAREZA_CONCISAO,
            FocoRefino.ENFASE_TECNICA,
            FocoRefino.IMPACTO,
        ]

    def test_tentativa_menor_que_um_gera_erro(self):
        with pytest.raises(ValueError, match="tentativa"):
            PedidoRefino(tentativa=0)

    def test_mais_de_tres_sugestoes_anteriores_gera_erro(self):
        with pytest.raises(ValueError, match="3 sugestões anteriores"):
            PedidoRefino(tentativa=5, sugestoes_anteriores=("a", "b", "c", "d"))

    def test_descarta_sugestoes_anteriores_em_branco(self):
        refino = PedidoRefino(tentativa=2, sugestoes_anteriores=(" Versão 1 ", "  "))

        assert refino.sugestoes_anteriores == ("Versão 1",)


class TestSugestaoRefinada:
    def test_guarda_o_valor_sugerido_e_o_foco_usado(self):
        sugestao = SugestaoRefinada(valor="Texto.", foco=FocoRefino.IMPACTO)

        assert sugestao.valor == "Texto."
        assert sugestao.foco == FocoRefino.IMPACTO
