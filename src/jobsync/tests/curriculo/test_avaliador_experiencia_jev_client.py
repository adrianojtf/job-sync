from jobsync.curriculo import ExperienciaParaAvaliacao
from jobsync.curriculo.adapters.avaliador_experiencia_jev_client import (
    AvaliadorExperienciaJevClient,
)
from jobsync.shared_kernel.adapters.cliente_jev_client import RespostaScoreJev


class ClienteJevFake:
    def __init__(self, respostas):
        self.respostas = respostas
        self.estado = None
        self.perguntas = None

    def avaliar_scores(self, estado, perguntas):
        self.estado = estado
        self.perguntas = perguntas
        return self.respostas


def _resposta_score(score: float) -> RespostaScoreJev:
    legenda = {
        0: "muito insuficiente",
        1: "insuficiente",
        2: "parcial",
        3: "adequado",
        4: "muito adequado",
    }
    probabilidades = {nivel: 0.05 for nivel in legenda}
    probabilidades[int(score)] = 0.8
    return RespostaScoreJev(
        pontuacao=score,
        probabilidades=probabilidades,
        confianca=0.85,
        legenda=legenda,
    )


class TestAvaliadorExperienciaJevClient:
    def test_avalia_quatro_dimensoes_com_contexto_da_vaga(self):
        experiencia = ExperienciaParaAvaliacao(
            descricao="Desenvolvi serviços Python para processamento de dados.",
            cargo="Pessoa desenvolvedora backend",
            empresa="TechCorp",
            periodo="2022-2025",
        )
        respostas = {
            "clareza_escrita": _resposta_score(3),
            "qualidade_detalhe": _resposta_score(4),
            "aderencia_vaga": _resposta_score(2),
            "consistencia_textual": _resposta_score(3),
        }
        cliente_jev = ClienteJevFake(respostas)
        avaliador = AvaliadorExperienciaJevClient(cliente_jev=cliente_jev)
        descricao_vaga = "Vaga de backend com Python e APIs."

        avaliacao = avaliador.avaliar(experiencia, descricao_vaga)

        assert cliente_jev.estado == {
            "experiencia_profissional": {
                "cargo": "Pessoa desenvolvedora backend",
                "empresa": "TechCorp",
                "periodo": "2022-2025",
                "descricao": "Desenvolvi serviços Python para processamento de dados.",
            },
            "descricao_vaga": descricao_vaga,
        }
        assert set(cliente_jev.perguntas) == {
            "clareza_escrita",
            "qualidade_detalhe",
            "aderencia_vaga",
            "consistencia_textual",
        }
        assert avaliacao.clareza_escrita.score == 75
        assert avaliacao.qualidade_detalhe.score == 100
        assert avaliacao.aderencia_vaga.score == 50
        assert avaliacao.consistencia_textual.score == 75
        assert avaliacao.score == 75

    def test_consistencia_textual_nao_instrui_verificacao_externa(self):
        cliente_jev = ClienteJevFake(
            {
                nome: _resposta_score(3)
                for nome in (
                    "clareza_escrita",
                    "qualidade_detalhe",
                    "aderencia_vaga",
                    "consistencia_textual",
                )
            }
        )
        avaliador = AvaliadorExperienciaJevClient(cliente_jev=cliente_jev)

        avaliador.avaliar(
            ExperienciaParaAvaliacao(descricao="Texto da experiência."),
            "Descrição da vaga.",
        )

        instrucoes = cliente_jev.perguntas["consistencia_textual"].instrucoes.lower()
        assert "não verifique fatos externamente" in instrucoes
