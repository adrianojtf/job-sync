"""Cliente compartilhado para decisões estruturadas do Jev."""
from __future__ import annotations

import math
import os
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Callable

from jobsync.shared_kernel.domain.score_avaliacao import ResultadoDimensaoAvaliacao

MODELO_PADRAO = "jev-1.14.0"


@dataclass(frozen=True)
class PerguntaScore:
    instrucoes: str
    criterios: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.instrucoes, str) or not self.instrucoes.strip():
            raise ValueError("As instruções da pergunta de score são obrigatórias.")
        if len(self.criterios) != 5 or any(
            not isinstance(criterio, str) or not criterio.strip()
            for criterio in self.criterios
        ):
            raise ValueError("A rubrica deve conter exatamente cinco níveis não vazios.")


@dataclass(frozen=True)
class RespostaScoreJev:
    pontuacao: float
    probabilidades: Mapping[int | str, float]
    confianca: float
    legenda: Mapping[int | str, str]

    def normalizar(self) -> ResultadoDimensaoAvaliacao:
        return ResultadoDimensaoAvaliacao.normalizar(
            pontuacao_ordinal=self.pontuacao,
            probabilidades=self.probabilidades,
            legenda=self.legenda,
            confianca=self.confianca,
        )


class ClienteJev:
    """Encapsula criação de perguntas Score e chamadas ao SDK TypeSafe."""

    def __init__(
        self,
        chave_api: str | None = None,
        modelo: str | None = None,
        cliente: Any | None = None,
        fabrica_score: Callable[..., Any] | None = None,
    ) -> None:
        self._modelo = modelo or os.getenv("TYPESAFE_MODEL") or MODELO_PADRAO
        self._fabrica_score = fabrica_score
        if cliente is not None:
            self._cliente = cliente
            return

        chave = chave_api or os.getenv("TYPESAFE_API_KEY")
        if not chave:
            raise ValueError("TYPESAFE_API_KEY não configurada.")

        try:
            from typesafe_sdk import Score, TypeSafeClient
        except ImportError as erro:
            raise RuntimeError("O SDK typesafe-sdk não está instalado.") from erro

        try:
            self._cliente = TypeSafeClient(api_key=chave, model=self._modelo)
        except Exception as erro:
            raise RuntimeError("Falha ao configurar o cliente Jev.") from erro
        self._fabrica_score = Score

    def avaliar_scores(
        self,
        estado: str | dict[str, Any],
        perguntas: Mapping[str, PerguntaScore],
    ) -> dict[str, RespostaScoreJev]:
        if not perguntas:
            raise ValueError("É necessário informar pelo menos uma pergunta de score.")
        if any(not nome.strip() for nome in perguntas):
            raise ValueError("O nome de cada pergunta de score é obrigatório.")
        fabrica_score = self._fabrica_score or self._obter_fabrica_score()
        perguntas_sdk = {
            nome: fabrica_score(
                instructions=pergunta.instrucoes,
                criteria=list(pergunta.criterios),
            )
            for nome, pergunta in perguntas.items()
        }

        try:
            resposta = self._cliente.system_one(state=estado, questions=perguntas_sdk)
        except Exception as erro:
            raise RuntimeError("Falha ao consultar o Jev.") from erro

        try:
            respostas_sdk = resposta.scores
            if not isinstance(respostas_sdk, Mapping):
                raise ValueError("A resposta de scores do Jev não é um mapeamento.")
            return {
                nome: self._mapear_resposta(respostas_sdk[nome])
                for nome in perguntas
            }
        except (AttributeError, KeyError, TypeError, ValueError, OverflowError) as erro:
            raise ValueError("Resposta de score inválida recebida do Jev.") from erro

    @staticmethod
    def _obter_fabrica_score() -> Callable[..., Any]:
        try:
            from typesafe_sdk import Score
        except ImportError as erro:
            raise RuntimeError("O SDK typesafe-sdk não está instalado.") from erro
        return Score

    @staticmethod
    def _mapear_resposta(resposta: Any) -> RespostaScoreJev:
        pontuacao = float(resposta.score)
        confianca = float(resposta.confidence)
        probabilidades = {
            int(nivel): float(probabilidade)
            for nivel, probabilidade in resposta.probabilities.items()
        }
        legenda = {
            int(nivel): rotulo
            for nivel, rotulo in resposta.legend.items()
        }
        if not math.isfinite(pontuacao) or not math.isfinite(confianca):
            raise ValueError("A resposta numérica do Jev deve ser finita.")
        return RespostaScoreJev(
            pontuacao=pontuacao,
            probabilidades=probabilidades,
            confianca=confianca,
            legenda=legenda,
        )
