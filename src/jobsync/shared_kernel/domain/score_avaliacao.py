"""Value objects e regras puras para scores estruturados de avaliações."""
from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class ResultadoDimensaoAvaliacao:
    """Resultado normalizado de uma dimensão avaliada."""

    score: int
    nivel: str
    confianca: float

    def __post_init__(self) -> None:
        if not isinstance(self.score, int) or isinstance(self.score, bool) or not 0 <= self.score <= 100:
            raise ValueError("O score da dimensão deve estar entre 0 e 100.")
        if not isinstance(self.nivel, str) or not self.nivel.strip():
            raise ValueError("O nível da dimensão não pode ser vazio.")
        if (
            isinstance(self.confianca, bool)
            or not isinstance(self.confianca, (int, float))
            or not math.isfinite(self.confianca)
            or not 0 <= self.confianca <= 1
        ):
            raise ValueError("A confiança deve estar entre 0 e 1.")

    @classmethod
    def normalizar(
        cls,
        pontuacao_ordinal: float,
        probabilidades: Mapping[int | str, float],
        legenda: Mapping[int | str, str],
        confianca: float,
    ) -> "ResultadoDimensaoAvaliacao":
        """Normaliza score esperado e escolhe o rótulo mais provável.

        Em caso de empate, a categoria ordinal inferior é escolhida.
        """
        if isinstance(pontuacao_ordinal, bool) or isinstance(confianca, bool):
            raise ValueError("A pontuação e a confiança devem ser numéricas.")
        try:
            pontuacao_ordinal = float(pontuacao_ordinal)
            confianca = float(confianca)
        except (TypeError, ValueError, OverflowError) as erro:
            raise ValueError("A pontuação e a confiança devem ser numéricas.") from erro

        niveis = cls._normalizar_legenda(legenda)
        distribuicao = cls._normalizar_probabilidades(probabilidades)
        if set(distribuicao) != set(niveis):
            raise ValueError("As probabilidades devem corresponder a todos os níveis.")

        nivel_maximo = max(niveis)
        if nivel_maximo != 4:
            raise ValueError("A escala ordinal deve conter os cinco níveis de 0 a 4.")
        if not math.isfinite(pontuacao_ordinal) or not 0 <= pontuacao_ordinal <= nivel_maximo:
            raise ValueError("A pontuação ordinal está fora do intervalo da escala.")
        if not math.isfinite(confianca) or not 0 <= confianca <= 1:
            raise ValueError("A confiança deve estar entre 0 e 1.")

        nivel_mais_provavel = min(
            distribuicao,
            key=lambda nivel: (-distribuicao[nivel], nivel),
        )
        return cls(
            score=round(pontuacao_ordinal / nivel_maximo * 100),
            nivel=niveis[nivel_mais_provavel],
            confianca=confianca,
        )

    @staticmethod
    def _normalizar_legenda(legenda: Mapping[int | str, str]) -> dict[int, str]:
        if not isinstance(legenda, Mapping):
            raise ValueError("A legenda da escala é inválida.")
        try:
            niveis = {int(chave): valor for chave, valor in legenda.items()}
        except (TypeError, ValueError) as erro:
            raise ValueError("A legenda contém um nível inválido.") from erro

        if len(niveis) != len(legenda):
            raise ValueError("A legenda contém níveis duplicados.")
        if not niveis or sorted(niveis) != list(range(len(niveis))):
            raise ValueError("A legenda deve conter níveis ordinais consecutivos a partir de zero.")
        if any(not isinstance(valor, str) or not valor.strip() for valor in niveis.values()):
            raise ValueError("Cada nível da legenda deve ter um rótulo textual.")
        return niveis

    @staticmethod
    def _normalizar_probabilidades(
        probabilidades: Mapping[int | str, float],
    ) -> dict[int, float]:
        if not isinstance(probabilidades, Mapping):
            raise ValueError("A distribuição de probabilidades é inválida.")
        try:
            valores = {int(chave): float(valor) for chave, valor in probabilidades.items()}
        except (TypeError, ValueError, OverflowError) as erro:
            raise ValueError("A distribuição de probabilidades é inválida.") from erro

        if len(valores) != len(probabilidades):
            raise ValueError("A distribuição contém níveis duplicados.")
        if not valores or any(
            not math.isfinite(valor) or not 0 <= valor <= 1 for valor in valores.values()
        ):
            raise ValueError("As probabilidades devem estar entre 0 e 1.")
        if not math.isclose(sum(valores.values()), 1.0, rel_tol=1e-3, abs_tol=1e-3):
            raise ValueError("A soma das probabilidades deve ser 1.")
        return valores


def calcular_score_geral(
    dimensoes: tuple[ResultadoDimensaoAvaliacao, ...],
) -> int:
    """Calcula a média aritmética, arredondada, das dimensões avaliadas."""
    if not dimensoes:
        raise ValueError("A avaliação deve conter pelo menos uma dimensão.")
    return round(sum(dimensao.score for dimensao in dimensoes) / len(dimensoes))
