"""Testes do Value Object ContextoVaga."""
import pytest

from jobsync.curriculo import ContextoVaga
from jobsync.vaga import AnaliseVaga


def _analise() -> AnaliseVaga:
    return AnaliseVaga(requisitos=(), ambiguidade=(), texto_original="Vaga Python")


class TestContextoVaga:
    def test_cria_contexto_com_descricao_idioma_e_analise(self):
        analise = _analise()

        contexto = ContextoVaga(
            descricao_vaga="Vaga Python", idioma_alvo="en", analise_vaga=analise
        )

        assert contexto.descricao_vaga == "Vaga Python"
        assert contexto.idioma_alvo == "en"
        assert contexto.analise_vaga is analise

    def test_descricao_vazia_gera_erro(self):
        with pytest.raises(ValueError, match="descrição da vaga"):
            ContextoVaga(descricao_vaga="  ", idioma_alvo="pt", analise_vaga=_analise())

    def test_idioma_nao_suportado_gera_erro(self):
        with pytest.raises(ValueError, match="idioma"):
            ContextoVaga(descricao_vaga="Vaga", idioma_alvo="fr", analise_vaga=_analise())

    def test_cargo_alvo_e_opcional_e_vazio_por_padrao(self):
        contexto = ContextoVaga(descricao_vaga="Vaga", idioma_alvo="pt", analise_vaga=_analise())

        assert contexto.cargo_alvo == ""

    def test_cargo_alvo_e_aparado(self):
        contexto = ContextoVaga(
            descricao_vaga="Vaga",
            idioma_alvo="pt",
            analise_vaga=_analise(),
            cargo_alvo="  Code Reviewer  ",
        )

        assert contexto.cargo_alvo == "Code Reviewer"
