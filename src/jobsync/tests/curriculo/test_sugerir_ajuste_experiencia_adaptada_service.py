"""Testes do caso de uso SugerirAjusteExperienciaAdaptada."""
from unittest.mock import Mock

import pytest

from jobsync.curriculo import AjustadorExperienciaPort, ContextoVaga, ExperienciaAdaptada
from jobsync.curriculo.service_layer.sugerir_ajuste_experiencia_adaptada import (
    SugerirAjusteExperienciaAdaptada,
)
from jobsync.curriculo.service_layer.sugestao_ia_indisponivel import SugestaoIAIndisponivel
from jobsync.vaga import AnaliseVaga


def _contexto() -> ContextoVaga:
    return ContextoVaga(
        descricao_vaga="Vaga Python",
        idioma_alvo="en",
        analise_vaga=AnaliseVaga(requisitos=(), ambiguidade=(), texto_original="Vaga Python"),
    )


def _experiencia(**sobrescritas) -> ExperienciaAdaptada:
    valores = {
        "cargo": "Dev",
        "empresa": "TechCorp",
        "periodo": "2024",
        "conquistas": ("Criei APIs editadas.",),
        "contexto": "Contexto editado.",
    }
    valores.update(sobrescritas)
    return ExperienciaAdaptada(**valores)


def _caso_de_uso() -> tuple[SugerirAjusteExperienciaAdaptada, Mock]:
    ajustador = Mock(spec=AjustadorExperienciaPort)
    return SugerirAjusteExperienciaAdaptada(ajustador), ajustador


class TestSugerirAjusteExperienciaAdaptada:
    def test_refina_as_conquistas_e_o_contexto_atuais_para_a_vaga(self):
        caso_de_uso, ajustador = _caso_de_uso()
        contexto = _contexto()
        ajustador.refinar.return_value = _experiencia(
            conquistas=("Sugestão A.", "Sugestão B."), contexto="Contexto sugerido."
        )

        resultado = caso_de_uso.executar(_experiencia(), contexto)

        ajustador.refinar.assert_called_once_with(experiencia=_experiencia(), contexto=contexto)
        assert resultado.conquistas == ("Sugestão A.", "Sugestão B.")
        assert resultado.contexto == "Contexto sugerido."

    def test_preserva_cargo_empresa_e_periodo_do_input(self):
        caso_de_uso, ajustador = _caso_de_uso()
        ajustador.refinar.return_value = ExperienciaAdaptada(
            cargo="Outro", empresa="Outra", periodo="1999", conquistas=("Sugestão.",)
        )

        resultado = caso_de_uso.executar(_experiencia(), _contexto())

        assert (resultado.cargo, resultado.empresa, resultado.periodo) == ("Dev", "TechCorp", "2024")
        assert resultado.conquistas == ("Sugestão.",)

    def test_aceita_experiencia_so_com_contexto(self):
        caso_de_uso, ajustador = _caso_de_uso()
        ajustador.refinar.return_value = _experiencia()

        caso_de_uso.executar(_experiencia(conquistas=()), _contexto())

        ajustador.refinar.assert_called_once()

    def test_aceita_experiencia_so_com_conquistas(self):
        caso_de_uso, ajustador = _caso_de_uso()
        ajustador.refinar.return_value = _experiencia()

        caso_de_uso.executar(_experiencia(contexto=""), _contexto())

        ajustador.refinar.assert_called_once()

    def test_sem_conquistas_e_sem_contexto_nao_chama_a_ia(self):
        caso_de_uso, ajustador = _caso_de_uso()

        with pytest.raises(ValueError, match="conquista ou o contexto"):
            caso_de_uso.executar(_experiencia(conquistas=(), contexto="  "), _contexto())

        ajustador.refinar.assert_not_called()

    def test_texto_acima_do_limite_nao_chama_a_ia(self):
        caso_de_uso, ajustador = _caso_de_uso()

        with pytest.raises(ValueError, match="5000"):
            caso_de_uso.executar(_experiencia(contexto="a" * 5001), _contexto())

        ajustador.refinar.assert_not_called()

    def test_o_limite_vale_para_o_texto_total_de_conquistas_e_contexto(self):
        caso_de_uso, ajustador = _caso_de_uso()
        conquistas = tuple("b" * 1000 for _ in range(5))

        with pytest.raises(ValueError, match="5000"):
            caso_de_uso.executar(_experiencia(conquistas=conquistas, contexto="c" * 100), _contexto())

        ajustador.refinar.assert_not_called()

    @pytest.mark.parametrize("erro", [RuntimeError("falha"), ValueError("resposta inválida")])
    def test_falha_do_provedor_vira_sugestao_indisponivel(self, erro):
        caso_de_uso, ajustador = _caso_de_uso()
        ajustador.refinar.side_effect = erro

        with pytest.raises(SugestaoIAIndisponivel):
            caso_de_uso.executar(_experiencia(), _contexto())
