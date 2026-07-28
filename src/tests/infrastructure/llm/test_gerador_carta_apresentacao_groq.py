"""Testes para o adaptador GeradorCartaApresentacaoGroq."""

import pytest

from domain.curriculo import Curriculo, SecaoCurriculo, TipoSecao
from domain.vaga import (
    AnaliseVaga,
    CategoriaRequisitoTecnico,
    OrigemRequisitoTecnico,
    RequisitoTecnico,
    TipoRequisitoTecnico,
)
from infrastructure.llm.gerador_carta_apresentacao_groq import GeradorCartaApresentacaoGroq


class ClienteGroqFake:
    def __init__(self, resposta):
        self.resposta = resposta
        self.prompt_usuario: str | None = None

    def solicitar_json(self, prompt_sistema: str, prompt_usuario: str) -> dict:
        self.prompt_usuario = prompt_usuario
        return self.resposta


def _curriculo() -> Curriculo:
    return Curriculo(
        nome_completo="Fulano de Tal",
        email="fulano@example.com",
        linkedin="linkedin.com/in/fulano",
        secoes=(
            SecaoCurriculo(TipoSecao.PERFIL, "Perfil", "Engenheiro backend com 5 anos de experiência."),
            SecaoCurriculo(TipoSecao.TECNOLOGIAS, "Tecnologias", "Python, Docker"),
        ),
    )


def _analise_vaga() -> AnaliseVaga:
    return AnaliseVaga(
        requisitos=(
            RequisitoTecnico(
                nome="Python",
                categoria=CategoriaRequisitoTecnico.TECNOLOGIA,
                tipo=TipoRequisitoTecnico.EXPLICITO,
                origem=OrigemRequisitoTecnico.DESCRICAO_VAGA,
            ),
            RequisitoTecnico(
                nome="Liderança técnica",
                categoria=CategoriaRequisitoTecnico.HABILIDADE,
                tipo=TipoRequisitoTecnico.IMPLICITO,
                origem=OrigemRequisitoTecnico.INTERPRETACAO,
            ),
        ),
        ambiguidade=(),
        texto_original="Vaga para desenvolvedor backend Python sênior.",
    )


class TestGeradorCartaApresentacaoGroq:
    def test_prompt_inclui_requisitos_explicitos_e_implicitos(self):
        cliente_fake = ClienteGroqFake({"carta": "Prezados, ..."})
        gerador = GeradorCartaApresentacaoGroq(cliente_groq=cliente_fake)

        carta = gerador.gerar(_curriculo(), _analise_vaga(), idioma_alvo="pt")

        assert carta == "Prezados, ..."
        prompt_text = cliente_fake.prompt_usuario.lower()
        assert "requisitos explícitos: python" in prompt_text
        assert "requisitos implícitos: liderança técnica" in prompt_text

    def test_idioma_alvo_reflete_no_prompt(self):
        cliente_fake = ClienteGroqFake({"carta": "Dear hiring manager, ..."})
        gerador = GeradorCartaApresentacaoGroq(cliente_groq=cliente_fake)

        gerador.gerar(_curriculo(), _analise_vaga(), idioma_alvo="en")

        prompt_text = cliente_fake.prompt_usuario.lower()
        assert "inglês (formato americano)" in prompt_text

    def test_resposta_vazia_do_modelo_gera_erro(self):
        cliente_fake = ClienteGroqFake({"carta": "   "})
        gerador = GeradorCartaApresentacaoGroq(cliente_groq=cliente_fake)

        with pytest.raises(ValueError):
            gerador.gerar(_curriculo(), _analise_vaga(), idioma_alvo="pt")

    def test_resposta_estruturada_em_dict_nao_quebra(self):
        """Regressão: o modelo às vezes devolve um objeto em vez de texto puro no campo 'carta'."""
        cliente_fake = ClienteGroqFake({"carta": {"saudacao": "Prezados", "corpo": "..."}})
        gerador = GeradorCartaApresentacaoGroq(cliente_groq=cliente_fake)

        carta = gerador.gerar(_curriculo(), _analise_vaga(), idioma_alvo="pt")

        assert "Prezados" in carta
