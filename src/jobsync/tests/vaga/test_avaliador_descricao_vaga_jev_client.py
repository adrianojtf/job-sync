from jobsync.shared_kernel.adapters.cliente_jev_client import RespostaScoreJev
from jobsync.vaga.adapters.avaliador_descricao_vaga_jev_client import (
    AvaliadorDescricaoVagaJevClient,
)


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
    probabilidades = {nivel_ordinal: 0.05 for nivel_ordinal in legenda}
    probabilidades[int(score)] = 0.8
    return RespostaScoreJev(
        pontuacao=score,
        probabilidades=probabilidades,
        confianca=0.85,
        legenda=legenda,
    )


class TestAvaliadorDescricaoVagaJevClient:
    def test_avalia_quatro_dimensoes_e_mapeia_resultado_de_dominio(self):
        respostas = {
            "completude": _resposta_score(3),
            "clareza": _resposta_score(4),
            "relevancia": _resposta_score(2),
            "inclusao": _resposta_score(3),
        }
        cliente_jev = ClienteJevFake(respostas)
        avaliador = AvaliadorDescricaoVagaJevClient(cliente_jev=cliente_jev)
        descricao = "Pessoa desenvolvedora Python com experiência em APIs."

        avaliacao = avaliador.avaliar(descricao)

        assert cliente_jev.estado == descricao
        assert set(cliente_jev.perguntas) == {
            "completude",
            "clareza",
            "relevancia",
            "inclusao",
        }
        assert all(len(pergunta.criterios) == 5 for pergunta in cliente_jev.perguntas.values())
        assert avaliacao.completude.score == 75
        assert avaliacao.clareza.score == 100
        assert avaliacao.relevancia.score == 50
        assert avaliacao.inclusao.score == 75
        assert avaliacao.score == 75

    def test_rubrica_de_inclusao_premia_linguagem_neutra(self):
        cliente_jev = ClienteJevFake(
            {
                "completude": _resposta_score(2),
                "clareza": _resposta_score(2),
                "relevancia": _resposta_score(2),
                "inclusao": _resposta_score(4),
            }
        )
        avaliador = AvaliadorDescricaoVagaJevClient(cliente_jev=cliente_jev)

        avaliador.avaliar("Descrição da vaga.")

        criterios = cliente_jev.perguntas["inclusao"].criterios
        assert "Muito excludente" in criterios[0]
        assert "Muito inclusiva" in criterios[4]
