"""Testes do caso de uso SugerirAjusteExperiencia (modo Meu perfil, sem vaga)."""
from unittest.mock import Mock

import pytest

from jobsync.curriculo import ExperienciaParaAvaliacao, FocoRefino, MelhoradorTextoCurriculoPort, PedidoRefino
from jobsync.curriculo.service_layer.sugerir_ajuste_experiencia import SugerirAjusteExperiencia
from jobsync.curriculo.service_layer.sugestao_ia_indisponivel import SugestaoIAIndisponivel


def _experiencia(descricao: str = "Descrição editada.") -> ExperienciaParaAvaliacao:
    return ExperienciaParaAvaliacao(
        cargo="Dev", empresa="TechCorp", periodo="2024", descricao=descricao
    )


def _caso_de_uso() -> tuple[SugerirAjusteExperiencia, Mock]:
    melhorador = Mock(spec=MelhoradorTextoCurriculoPort)
    return SugerirAjusteExperiencia(melhorador), melhorador


class TestSugerirAjusteExperiencia:
    def test_melhora_a_escrita_da_descricao_recebida(self):
        caso_de_uso, melhorador = _caso_de_uso()
        melhorador.melhorar_experiencia.return_value = _experiencia("Sugestão sem vaga.")

        resultado = caso_de_uso.executar(_experiencia())

        melhorador.melhorar_experiencia.assert_called_once_with(_experiencia(), PedidoRefino())
        assert resultado.valor.descricao == "Sugestão sem vaga."
        assert resultado.foco == FocoRefino.IMPACTO

    def test_preserva_cargo_empresa_e_periodo_do_input(self):
        caso_de_uso, melhorador = _caso_de_uso()
        melhorador.melhorar_experiencia.return_value = ExperienciaParaAvaliacao(
            cargo="Outro", empresa="Outra", periodo="1999", descricao="Sugestão."
        )

        resultado = caso_de_uso.executar(_experiencia())

        assert resultado.valor == ExperienciaParaAvaliacao(
            cargo="Dev", empresa="TechCorp", periodo="2024", descricao="Sugestão."
        )

    def test_descricao_vazia_nao_chama_a_ia(self):
        caso_de_uso, melhorador = _caso_de_uso()

        with pytest.raises(ValueError, match="descrição"):
            caso_de_uso.executar(_experiencia("  "))

        melhorador.melhorar_experiencia.assert_not_called()

    def test_descricao_acima_do_limite_nao_chama_a_ia(self):
        caso_de_uso, melhorador = _caso_de_uso()

        with pytest.raises(ValueError, match="5000"):
            caso_de_uso.executar(_experiencia("a" * 5001))

        melhorador.melhorar_experiencia.assert_not_called()

    @pytest.mark.parametrize("erro", [RuntimeError("falha"), ValueError("resposta inválida")])
    def test_falha_do_provedor_vira_sugestao_indisponivel(self, erro):
        caso_de_uso, melhorador = _caso_de_uso()
        melhorador.melhorar_experiencia.side_effect = erro

        with pytest.raises(SugestaoIAIndisponivel):
            caso_de_uso.executar(_experiencia())


class TestSugerirAjusteExperienciaRefino:
    def test_repassa_o_refino_e_devolve_o_foco_sem_vaga(self):
        caso_de_uso, melhorador = _caso_de_uso()
        refino = PedidoRefino(tentativa=2, sugestoes_anteriores=("Versão 1.",))
        melhorador.melhorar_experiencia.return_value = _experiencia("Versão 2.")

        resultado = caso_de_uso.executar(_experiencia(), refino)

        melhorador.melhorar_experiencia.assert_called_once_with(_experiencia(), refino)
        assert resultado.foco == FocoRefino.CLAREZA_CONCISAO

    def test_sugestao_anterior_acima_do_limite_nao_chama_a_ia(self):
        caso_de_uso, melhorador = _caso_de_uso()

        with pytest.raises(ValueError, match="5000"):
            caso_de_uso.executar(_experiencia(), PedidoRefino(tentativa=2, sugestoes_anteriores=("a" * 5001,)))

        melhorador.melhorar_experiencia.assert_not_called()
