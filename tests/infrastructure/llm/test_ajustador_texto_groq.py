"""Testes para o adaptador AjustadorTextoGroq."""

from domain.analise_vaga import (
    AnaliseVaga,
    CategoriaRequisitoTecnico,
    OrigemRequisitoTecnico,
    RequisitoTecnico,
    TipoRequisitoTecnico,
)
from domain.curriculo import SecaoCurriculo, TipoSecao

from infrastructure.llm.ajustador_texto_groq import AjustadorTextoGroq


class ClienteGroqFake:
    def __init__(self, resposta):
        self.resposta = resposta
        self.prompt_usuario: str | None = None

    def solicitar_json(self, prompt_sistema: str, prompt_usuario: str) -> dict:
        self.prompt_usuario = prompt_usuario
        return self.resposta


def test_ajustador_texto_groq_usa_analise_vaga_estruturada_no_prompt() -> None:
    cliente_fake = ClienteGroqFake({"conteudo_ajustado": "Conteúdo ajustado"})
    ajustador = AjustadorTextoGroq(cliente_groq=cliente_fake)

    analise_vaga = AnaliseVaga(
        requisitos=(
            RequisitoTecnico(
                nome="Python",
                categoria=CategoriaRequisitoTecnico.TECNOLOGIA,
                tipo=TipoRequisitoTecnico.EXPLICITO,
                origem=OrigemRequisitoTecnico.DESCRICAO_VAGA,
            ),
            RequisitoTecnico(
                nome="Desenvolvimento web",
                categoria=CategoriaRequisitoTecnico.HABILIDADE,
                tipo=TipoRequisitoTecnico.IMPLICITO,
                origem=OrigemRequisitoTecnico.INTERPRETACAO,
            ),
        ),
        ambiguidade=("Desejável conhecimento em bancos de dados relacionais",),
        texto_original="Vaga para desenvolvedor backend com Python.",
    )

    secao = SecaoCurriculo(TipoSecao.TECNOLOGIAS, "Tecnologias", "Python, Django")
    secao_ajustada = ajustador.ajustar_secao(
        secao,
        descricao_vaga="Vaga para desenvolvedor backend com Python.",
        idioma_alvo="pt",
        analise_vaga=analise_vaga,
    )

    assert secao_ajustada.conteudo == "Conteúdo ajustado"
    assert cliente_fake.prompt_usuario is not None
    prompt_text = cliente_fake.prompt_usuario.lower()
    assert "requisitos explícitos: python" in prompt_text
    assert "requisitos implícitos: desenvolvimento web" in prompt_text
    assert "trechos ambíguos: desejável conhecimento em bancos de dados relacionais" in prompt_text
    assert "não infira frameworks, ferramentas ou habilidades" in prompt_text
