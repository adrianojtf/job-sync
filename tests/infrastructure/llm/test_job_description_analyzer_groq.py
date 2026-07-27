"""Testes para o adapter JobDescriptionAnalyzerGroq."""

from domain.analise_vaga import (
    CategoriaRequisitoTecnico,
    OrigemRequisitoTecnico,
    TipoRequisitoTecnico,
)

from infrastructure.llm.job_description_analyzer_groq import JobDescriptionAnalyzerGroq


class ClienteGroqFake:
    def __init__(self, resposta):
        self.resposta = resposta
        self.prompt_usuario: str | None = None

    def solicitar_json(self, prompt_sistema: str, prompt_usuario: str) -> dict:
        self.prompt_usuario = prompt_usuario
        if isinstance(self.resposta, Exception):
            raise self.resposta
        return self.resposta


def test_job_description_analyzer_groq_extrai_requisitos_explicitos_e_implicitose_ambiguidade() -> None:
    descricao_vaga = (
        "Vaga para desenvolvedor backend com Python e experiência em desenvolvimento web. "
        "Desejável conhecimento em bancos de dados relacionais e interesse em metodologias ágeis."
    )
    cliente_fake = ClienteGroqFake(
        resposta={
            "requisitos": [
                {
                    "nome": "Python",
                    "categoria": "tecnologia",
                    "tipo": "explicito",
                    "origem": "descricao_vaga",
                },
                {
                    "nome": "Desenvolvimento web",
                    "categoria": "habilidade",
                    "tipo": "implicito",
                    "origem": "interpretacao",
                },
            ],
            "ambiguidade": [
                "Desejável conhecimento em bancos de dados relacionais",
            ],
        }
    )
    analisador = JobDescriptionAnalyzerGroq(cliente_groq=cliente_fake)

    analise = analisador.analisar(descricao_vaga)

    assert analise.texto_original == descricao_vaga
    assert len(analise.requisitos) == 2
    primeiro_requisito = analise.requisitos[0]
    segundo_requisito = analise.requisitos[1]

    assert primeiro_requisito.nome == "python"
    assert primeiro_requisito.categoria == CategoriaRequisitoTecnico.TECNOLOGIA
    assert primeiro_requisito.tipo == TipoRequisitoTecnico.EXPLICITO
    assert primeiro_requisito.origem == OrigemRequisitoTecnico.DESCRICAO_VAGA

    assert segundo_requisito.nome == "desenvolvimento web"
    assert segundo_requisito.categoria == CategoriaRequisitoTecnico.HABILIDADE
    assert segundo_requisito.tipo == TipoRequisitoTecnico.IMPLICITO
    assert segundo_requisito.origem == OrigemRequisitoTecnico.INTERPRETACAO

    assert analise.ambiguidade == (
        "Desejável conhecimento em bancos de dados relacionais",
    )


def test_job_description_analyzer_groq_relanca_excecao_clara_quando_resposta_json_invalida() -> None:
    cliente_fake = ClienteGroqFake(ValueError("Resposta do modelo não é um JSON válido"))
    analisador = JobDescriptionAnalyzerGroq(cliente_groq=cliente_fake)

    try:
        analisador.analisar("Vaga para desenvolvedor Python.")
        assert False, "Esperava ValueError para resposta JSON inválida"
    except ValueError as erro:
        assert "Falha ao parsear a resposta do Groq" in str(erro)
        assert "Resposta do modelo não é um JSON válido" in str(erro)
