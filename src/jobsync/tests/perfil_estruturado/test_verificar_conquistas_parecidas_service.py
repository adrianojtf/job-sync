"""Testes do caso de uso VerificarConquistasParecidas."""

import pytest

from jobsync.perfil_estruturado.service_layer.verificar_conquistas_parecidas import (
    VerificarConquistasParecidas,
    VerificarConquistasParecidasInputDto,
)


class TestVerificarConquistasParecidas:
    def test_devolve_apenas_as_conquistas_parecidas(self):
        parecida = "Reduzi o tempo de deploy em 40% com pipeline automatizado."
        entrada = VerificarConquistasParecidasInputDto(
            texto="Reduzi o tempo de deploy com o pipeline automatizado",
            conquistas=(parecida, "Liderei a migração do banco de dados."),
        )

        resultado = VerificarConquistasParecidas().executar(entrada)

        assert resultado == (parecida,)

    def test_sem_conquistas_parecidas_devolve_tupla_vazia(self):
        entrada = VerificarConquistasParecidasInputDto(
            texto="Construí uma API de pagamentos.", conquistas=("Liderei a migração do banco de dados.",)
        )

        assert VerificarConquistasParecidas().executar(entrada) == ()

    def test_sem_conquistas_existentes_devolve_tupla_vazia(self):
        entrada = VerificarConquistasParecidasInputDto(texto="Construí uma API.", conquistas=())

        assert VerificarConquistasParecidas().executar(entrada) == ()

    @pytest.mark.parametrize("texto", ["", "   "])
    def test_texto_vazio_levanta_erro(self, texto):
        entrada = VerificarConquistasParecidasInputDto(texto=texto, conquistas=("Qualquer.",))

        with pytest.raises(ValueError, match="texto da conquista"):
            VerificarConquistasParecidas().executar(entrada)
