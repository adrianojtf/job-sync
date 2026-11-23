"""Testes do caso de uso RedigirConquistaDeLacuna."""
import pytest

from jobsync.curriculo.domain.lacuna_da_vaga import LacunaDaVaga
from jobsync.curriculo.domain.redator_conquista_port import RedatorConquistaPort
from jobsync.curriculo.service_layer.redigir_conquista_de_lacuna import (
    RedigirConquistaDeLacuna,
    RedigirConquistaDeLacunaInputDto,
)
from jobsync.curriculo.service_layer.sugestao_ia_indisponivel import SugestaoIAIndisponivel

LACUNA = LacunaDaVaga("Construção de MVPs", "Você já construiu um MVP do zero?")


class RedatorFake(RedatorConquistaPort):
    def __init__(self, texto: str = "Construí um MVP do zero.", erro: Exception | None = None):
        self._texto = texto
        self._erro = erro
        self.chamadas: list[tuple[LacunaDaVaga, str, str, str]] = []

    def redigir(self, lacuna: LacunaDaVaga, caso: str, cargo: str, idioma_alvo: str) -> str:
        self.chamadas.append((lacuna, caso, cargo, idioma_alvo))
        if self._erro is not None:
            raise self._erro
        return self._texto


def _entrada(caso: str = "Montei o MVP em 6 semanas.", idioma: str = "pt") -> RedigirConquistaDeLacunaInputDto:
    return RedigirConquistaDeLacunaInputDto(lacuna=LACUNA, caso=caso, cargo="Dev", idioma_alvo=idioma)


class TestRedigirConquistaDeLacuna:
    def test_devolve_o_texto_redigido_pela_porta(self):
        resultado = RedigirConquistaDeLacuna(RedatorFake("Construí um MVP do zero.")).executar(_entrada())

        assert resultado == "Construí um MVP do zero."

    def test_entrega_a_lacuna_o_caso_aparado_o_cargo_e_o_idioma_a_porta(self):
        redator = RedatorFake()

        RedigirConquistaDeLacuna(redator).executar(_entrada(caso="  Montei o MVP em 6 semanas.  "))

        assert redator.chamadas == [(LACUNA, "Montei o MVP em 6 semanas.", "Dev", "pt")]

    @pytest.mark.parametrize("caso", ["", "   "])
    def test_caso_vazio_levanta_erro_sem_chamar_a_ia(self, caso):
        redator = RedatorFake()

        with pytest.raises(ValueError, match="caso"):
            RedigirConquistaDeLacuna(redator).executar(_entrada(caso=caso))

        assert redator.chamadas == []

    def test_idioma_nao_suportado_levanta_erro(self):
        with pytest.raises(ValueError):
            RedigirConquistaDeLacuna(RedatorFake()).executar(_entrada(idioma="fr"))

    @pytest.mark.parametrize("erro", [RuntimeError("falha"), ValueError("formato")])
    def test_falha_da_ia_vira_sugestao_indisponivel(self, erro):
        with pytest.raises(SugestaoIAIndisponivel):
            RedigirConquistaDeLacuna(RedatorFake(erro=erro)).executar(_entrada())
