"""Testes para o adaptador GeradorSugestoesAtsGroq."""

import pytest

from domain.ats_score import ResultadoAtsScore
from domain.curriculo import Curriculo, SecaoCurriculo, TipoSecao
from domain.vaga import (
    AnaliseVaga,
    CategoriaRequisitoTecnico,
    OrigemRequisitoTecnico,
    RequisitoTecnico,
    TipoRequisitoTecnico,
)
from infrastructure.llm.gerador_sugestoes_ats_groq import GeradorSugestoesAtsGroq


class ClienteGroqFake:
    def __init__(self, resposta):
        self.resposta = resposta
        self.prompt_usuario: str | None = None
        self.chamado = False

    def solicitar_json(self, prompt_sistema: str, prompt_usuario: str) -> dict:
        self.chamado = True
        self.prompt_usuario = prompt_usuario
        return self.resposta


def _curriculo() -> Curriculo:
    return Curriculo(
        nome_completo="Fulano de Tal",
        email="fulano@example.com",
        linkedin="linkedin.com/in/fulano",
        secoes=(SecaoCurriculo(TipoSecao.TECNOLOGIAS, "Tecnologias", "Python, containers com Docker"),),
    )


def _requisito(nome: str) -> RequisitoTecnico:
    return RequisitoTecnico(
        nome=nome,
        categoria=CategoriaRequisitoTecnico.TECNOLOGIA,
        tipo=TipoRequisitoTecnico.EXPLICITO,
        origem=OrigemRequisitoTecnico.DESCRICAO_VAGA,
    )


class TestGeradorSugestoesAtsGroq:
    def test_sem_requisitos_faltantes_nao_chama_a_ia(self):
        cliente_fake = ClienteGroqFake({"sugestoes": ["não deveria ser usado"]})
        gerador = GeradorSugestoesAtsGroq(cliente_groq=cliente_fake)
        analise = AnaliseVaga(requisitos=(), ambiguidade=(), texto_original="vaga qualquer")
        resultado_ats = ResultadoAtsScore(nota=100, requisitos_faltantes=())

        sugestoes = gerador.gerar(_curriculo(), analise, resultado_ats)

        assert cliente_fake.chamado is False
        assert len(sugestoes) == 1
        assert "Nenhuma mudança necessária" in sugestoes[0]

    def test_com_requisitos_faltantes_retorna_um_topico_por_item_da_lista(self):
        cliente_fake = ClienteGroqFake(
            {
                "sugestoes": [
                    "Kubernetes: adicione na seção de Tecnologias.",
                    "AWS: lacuna real, não há evidência no currículo.",
                ]
            }
        )
        gerador = GeradorSugestoesAtsGroq(cliente_groq=cliente_fake)
        analise = AnaliseVaga(requisitos=(), ambiguidade=(), texto_original="Vaga que exige Kubernetes e AWS")
        resultado_ats = ResultadoAtsScore(
            nota=50, requisitos_faltantes=(_requisito("Kubernetes"), _requisito("AWS"))
        )

        sugestoes = gerador.gerar(_curriculo(), analise, resultado_ats)

        assert sugestoes == (
            "Kubernetes: adicione na seção de Tecnologias.",
            "AWS: lacuna real, não há evidência no currículo.",
        )
        assert "kubernetes" in cliente_fake.prompt_usuario.lower()
        assert "docker" in cliente_fake.prompt_usuario.lower()

    def test_resposta_vazia_do_modelo_gera_erro(self):
        cliente_fake = ClienteGroqFake({"sugestoes": []})
        gerador = GeradorSugestoesAtsGroq(cliente_groq=cliente_fake)
        analise = AnaliseVaga(requisitos=(), ambiguidade=(), texto_original="vaga")
        resultado_ats = ResultadoAtsScore(nota=50, requisitos_faltantes=(_requisito("Kubernetes"),))

        with pytest.raises(ValueError):
            gerador.gerar(_curriculo(), analise, resultado_ats)

    def test_resposta_como_texto_unico_e_aceita_como_um_topico(self):
        """Tolerância: se o modelo devolver uma string única em vez de lista, vira um tópico só."""
        cliente_fake = ClienteGroqFake({"sugestoes": "Adicione Kubernetes na seção de Tecnologias."})
        gerador = GeradorSugestoesAtsGroq(cliente_groq=cliente_fake)
        analise = AnaliseVaga(requisitos=(), ambiguidade=(), texto_original="vaga")
        resultado_ats = ResultadoAtsScore(nota=50, requisitos_faltantes=(_requisito("Kubernetes"),))

        sugestoes = gerador.gerar(_curriculo(), analise, resultado_ats)

        assert sugestoes == ("Adicione Kubernetes na seção de Tecnologias.",)

    def test_resposta_estruturada_em_dict_nao_quebra(self):
        """Regressão: o modelo às vezes devolve um objeto em vez de lista no campo 'sugestoes'."""
        cliente_fake = ClienteGroqFake(
            {"sugestoes": {"Kubernetes": "Considere mencionar experiência com orquestração de containers."}}
        )
        gerador = GeradorSugestoesAtsGroq(cliente_groq=cliente_fake)
        analise = AnaliseVaga(requisitos=(), ambiguidade=(), texto_original="vaga")
        resultado_ats = ResultadoAtsScore(nota=50, requisitos_faltantes=(_requisito("Kubernetes"),))

        sugestoes = gerador.gerar(_curriculo(), analise, resultado_ats)

        assert any("Kubernetes" in item for item in sugestoes)
