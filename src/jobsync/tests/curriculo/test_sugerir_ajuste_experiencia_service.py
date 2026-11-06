"""Testes do caso de uso SugerirAjusteExperiencia."""
from unittest.mock import Mock

import pytest

from jobsync.curriculo import (
    AjustadorExperienciaPort,
    ExperienciaAdaptada,
    ContextoVaga,
    ExperienciaParaAvaliacao,
    MelhoradorTextoCurriculoPort,
)
from jobsync.curriculo.service_layer.sugerir_ajuste_experiencia import SugerirAjusteExperiencia
from jobsync.curriculo.service_layer.sugestao_ia_indisponivel import SugestaoIAIndisponivel
from jobsync.vaga import AnaliseVaga


def _contexto() -> ContextoVaga:
    return ContextoVaga(
        descricao_vaga="Vaga Python",
        idioma_alvo="pt",
        analise_vaga=AnaliseVaga(requisitos=(), ambiguidade=(), texto_original="Vaga Python"),
    )


def _experiencia(descricao: str = "Descrição editada.") -> ExperienciaParaAvaliacao:
    return ExperienciaParaAvaliacao(
        cargo="Dev", empresa="TechCorp", periodo="2024", descricao=descricao
    )


def _adaptada(conquista: str, contexto: str = "") -> ExperienciaAdaptada:
    return ExperienciaAdaptada(
        cargo="Dev", empresa="TechCorp", periodo="2024", conquistas=(conquista,), contexto=contexto
    )


def _caso_de_uso() -> tuple[SugerirAjusteExperiencia, Mock, Mock]:
    ajustador = Mock(spec=AjustadorExperienciaPort)
    melhorador = Mock(spec=MelhoradorTextoCurriculoPort)
    return SugerirAjusteExperiencia(ajustador, melhorador), ajustador, melhorador


class TestSugerirAjusteExperiencia:
    def test_com_contexto_ajusta_a_descricao_recebida_para_a_vaga(self):
        caso_de_uso, ajustador, melhorador = _caso_de_uso()
        contexto = _contexto()
        ajustador.ajustar.return_value = _adaptada("Sugestão da IA.")

        resultado = caso_de_uso.executar(_experiencia(), contexto)

        ajustador.ajustar.assert_called_once_with(
            experiencia=_experiencia(),
            descricao_vaga="Vaga Python",
            idioma_alvo="pt",
            analise_vaga=contexto.analise_vaga,
        )
        melhorador.melhorar_experiencia.assert_not_called()
        assert resultado.descricao == "Sugestão da IA."

    def test_com_contexto_a_descricao_sugerida_inclui_conquistas_e_contexto_da_ia(self):
        caso_de_uso, ajustador, _ = _caso_de_uso()
        ajustador.ajustar.return_value = ExperienciaAdaptada(
            cargo="Dev",
            empresa="TechCorp",
            periodo="2024",
            conquistas=("Criei APIs.", "Reduzi custos."),
            contexto="Empresa de pagamentos.",
        )

        resultado = caso_de_uso.executar(_experiencia(), _contexto())

        assert resultado.descricao == "Criei APIs.\nReduzi custos.\nEmpresa de pagamentos."

    def test_sem_contexto_melhora_a_escrita_sem_vaga(self):
        caso_de_uso, ajustador, melhorador = _caso_de_uso()
        melhorador.melhorar_experiencia.return_value = _experiencia("Sugestão sem vaga.")

        resultado = caso_de_uso.executar(_experiencia(), None)

        melhorador.melhorar_experiencia.assert_called_once_with(_experiencia())
        ajustador.ajustar.assert_not_called()
        assert resultado.descricao == "Sugestão sem vaga."

    def test_preserva_cargo_empresa_e_periodo_do_input(self):
        caso_de_uso, ajustador, _ = _caso_de_uso()
        ajustador.ajustar.return_value = ExperienciaAdaptada(
            cargo="Outro", empresa="Outra", periodo="1999", conquistas=("Sugestão.",)
        )

        resultado = caso_de_uso.executar(_experiencia(), _contexto())

        assert resultado == ExperienciaParaAvaliacao(
            cargo="Dev", empresa="TechCorp", periodo="2024", descricao="Sugestão."
        )

    def test_descricao_vazia_nao_chama_a_ia(self):
        caso_de_uso, ajustador, melhorador = _caso_de_uso()

        with pytest.raises(ValueError, match="descrição"):
            caso_de_uso.executar(_experiencia("  "), _contexto())

        ajustador.ajustar.assert_not_called()
        melhorador.melhorar_experiencia.assert_not_called()

    def test_descricao_acima_do_limite_nao_chama_a_ia(self):
        caso_de_uso, ajustador, _ = _caso_de_uso()

        with pytest.raises(ValueError, match="5000"):
            caso_de_uso.executar(_experiencia("a" * 5001), _contexto())

        ajustador.ajustar.assert_not_called()

    @pytest.mark.parametrize("erro", [RuntimeError("falha"), ValueError("resposta inválida")])
    def test_falha_do_provedor_vira_sugestao_indisponivel(self, erro):
        caso_de_uso, _, melhorador = _caso_de_uso()
        melhorador.melhorar_experiencia.side_effect = erro

        with pytest.raises(SugestaoIAIndisponivel):
            caso_de_uso.executar(_experiencia(), None)
