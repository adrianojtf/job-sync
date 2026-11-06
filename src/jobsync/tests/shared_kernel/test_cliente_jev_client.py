import os
import sys
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from jobsync.shared_kernel.adapters.cliente_jev_client import (
    MODELO_PADRAO,
    ClienteJev,
    PerguntaScore,
)


class ScoreFake:
    def __init__(self, instructions: str, criteria: list[str]):
        self.instructions = instructions
        self.criteria = criteria


class TypeSafeClientFake:
    def __init__(self, scores=None, erro: Exception | None = None):
        self._scores = scores or {}
        self._erro = erro
        self.estado = None
        self.perguntas = None

    def system_one(self, state, questions):
        self.estado = state
        self.perguntas = questions
        if self._erro is not None:
            raise self._erro
        return SimpleNamespace(scores=self._scores)


def _resposta_score():
    return SimpleNamespace(
        score=2.5,
        probabilities={0: 0.1, 1: 0.2, 2: 0.3, 3: 0.3, 4: 0.1},
        confidence=0.75,
        legend={
            0: "muito insuficiente",
            1: "insuficiente",
            2: "parcial",
            3: "adequado",
            4: "muito bom",
        },
    )


class TestClienteJev:
    def test_envia_perguntas_score_e_normaliza_respostas(self):
        resposta_score = _resposta_score()
        sdk_client = TypeSafeClientFake(
            scores={"clareza": resposta_score, "relevancia": resposta_score}
        )
        cliente = ClienteJev(cliente=sdk_client, fabrica_score=ScoreFake)
        perguntas = {
            "clareza": PerguntaScore(
                instrucoes="Avalie a clareza.",
                criterios=("muito baixo", "baixo", "medio", "alto", "muito alto"),
            ),
            "relevancia": PerguntaScore(
                instrucoes="Avalie a relevancia.",
                criterios=("muito baixa", "baixa", "media", "alta", "muito alta"),
            ),
        }

        respostas = cliente.avaliar_scores(
            estado={"descricao": "Texto a avaliar."},
            perguntas=perguntas,
        )

        assert sdk_client.estado == {"descricao": "Texto a avaliar."}
        assert sdk_client.perguntas["clareza"].instructions == "Avalie a clareza."
        assert sdk_client.perguntas["clareza"].criteria == [
            "muito baixo",
            "baixo",
            "medio",
            "alto",
            "muito alto",
        ]
        assert respostas["clareza"].normalizar().score == 62
        assert respostas["clareza"].normalizar().nivel == "parcial"
        assert respostas["clareza"].normalizar().confianca == 0.75

    def test_nao_chama_o_sdk_sem_perguntas(self):
        sdk_client = TypeSafeClientFake()
        cliente = ClienteJev(cliente=sdk_client, fabrica_score=ScoreFake)

        with pytest.raises(ValueError, match="pelo menos uma pergunta"):
            cliente.avaliar_scores("estado", {})

        assert sdk_client.estado is None

    @pytest.mark.parametrize(
        "erro",
        [
            TimeoutError("timeout com detalhe"),
            PermissionError("credencial inválida"),
        ],
    )
    def test_traduz_falha_do_sdk_sem_expor_detalhes(self, erro):
        sdk_client = TypeSafeClientFake(erro=erro)
        cliente = ClienteJev(cliente=sdk_client, fabrica_score=ScoreFake)
        perguntas = {
            "clareza": PerguntaScore(
                instrucoes="Avalie a clareza.",
                criterios=("muito baixo", "baixo", "medio", "alto", "muito alto"),
            )
        }

        with pytest.raises(RuntimeError, match="Falha ao consultar o Jev") as erro:
            cliente.avaliar_scores("estado", perguntas)

        assert "timeout com detalhe" not in str(erro.value)
        assert "credencial inválida" not in str(erro.value)

    def test_resposta_sem_score_solicitado_e_rejeitada(self):
        cliente = ClienteJev(cliente=TypeSafeClientFake(), fabrica_score=ScoreFake)
        perguntas = {
            "clareza": PerguntaScore(
                instrucoes="Avalie a clareza.",
                criterios=("muito baixo", "baixo", "medio", "alto", "muito alto"),
            )
        }

        with pytest.raises(ValueError, match="Resposta de score inválida"):
            cliente.avaliar_scores("estado", perguntas)

    def test_resposta_com_campos_ausentes_e_rejeitada(self):
        resposta_sem_confianca = SimpleNamespace(score=2.0)
        sdk_client = TypeSafeClientFake(scores={"clareza": resposta_sem_confianca})
        cliente = ClienteJev(cliente=sdk_client, fabrica_score=ScoreFake)
        perguntas = {
            "clareza": PerguntaScore(
                instrucoes="Avalie a clareza.",
                criterios=("muito baixo", "baixo", "medio", "alto", "muito alto"),
            )
        }

        with pytest.raises(ValueError, match="Resposta de score inválida"):
            cliente.avaliar_scores("estado", perguntas)

    def test_configura_sdk_com_chave_e_modelo_do_ambiente(self):
        clientes = []

        class TypeSafeSDKFake:
            def __init__(self, api_key: str, model: str):
                clientes.append((api_key, model))

        sdk = SimpleNamespace(Score=ScoreFake, TypeSafeClient=TypeSafeSDKFake)
        with patch.dict(
            os.environ,
            {"TYPESAFE_API_KEY": "test-key", "TYPESAFE_MODEL": "jev-test"},
        ):
            with patch.dict(sys.modules, {"typesafe_sdk": sdk}):
                ClienteJev()

        assert clientes == [("test-key", "jev-test")]

    def test_modelo_padrao_e_jev_1_14(self):
        clientes = []

        class TypeSafeSDKFake:
            def __init__(self, api_key: str, model: str):
                clientes.append((api_key, model))

        sdk = SimpleNamespace(Score=ScoreFake, TypeSafeClient=TypeSafeSDKFake)
        with patch.dict(os.environ):
            os.environ.pop("TYPESAFE_MODEL", None)
            os.environ["TYPESAFE_API_KEY"] = "test-key"
            with patch.dict(sys.modules, {"typesafe_sdk": sdk}):
                ClienteJev()

        assert clientes == [("test-key", MODELO_PADRAO)]

    def test_chave_api_e_obrigatoria_sem_cliente_injetado(self):
        with patch.dict(os.environ):
            os.environ.pop("TYPESAFE_API_KEY", None)

            with pytest.raises(ValueError, match="TYPESAFE_API_KEY"):
                ClienteJev()

    def test_pergunta_score_rejeita_rubrica_invalida(self):
        with pytest.raises(ValueError, match="exatamente cinco níveis"):
            PerguntaScore(instrucoes="Avalie", criterios=("alto",))
