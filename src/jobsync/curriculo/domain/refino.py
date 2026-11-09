"""Value Objects: refino das sugestões de IA, com foco variável a cada pedido (JOB-0037).

Cada novo pedido de sugestão para o mesmo campo parte do texto atual e usa um foco
diferente do anterior, em rodízio pela tentativa. As sugestões já mostradas vão junto,
para a IA não repeti-las. O histórico vive só na tela; o backend não guarda estado.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Generic, TypeVar

MAXIMO_SUGESTOES_ANTERIORES = 3


class FocoRefino(str, Enum):
    ADERENCIA_VAGA = "aderencia_vaga"
    IMPACTO = "impacto"
    PALAVRAS_CHAVE = "palavras_chave"
    CLAREZA_CONCISAO = "clareza_concisao"
    ENFASE_TECNICA = "enfase_tecnica"


_RODIZIO_COM_VAGA = (
    FocoRefino.ADERENCIA_VAGA,
    FocoRefino.IMPACTO,
    FocoRefino.PALAVRAS_CHAVE,
    FocoRefino.CLAREZA_CONCISAO,
)
_RODIZIO_SEM_VAGA = (
    FocoRefino.IMPACTO,
    FocoRefino.CLAREZA_CONCISAO,
    FocoRefino.ENFASE_TECNICA,
)


@dataclass(frozen=True)
class PedidoRefino:
    tentativa: int = 1
    sugestoes_anteriores: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.tentativa < 1:
            raise ValueError("A tentativa de sugestão começa em 1.")
        anteriores = tuple(
            sugestao.strip() for sugestao in self.sugestoes_anteriores if sugestao and sugestao.strip()
        )
        if len(anteriores) > MAXIMO_SUGESTOES_ANTERIORES:
            raise ValueError(
                f"Envie no máximo {MAXIMO_SUGESTOES_ANTERIORES} sugestões anteriores."
            )
        object.__setattr__(self, "sugestoes_anteriores", anteriores)

    def foco(self, com_vaga: bool) -> FocoRefino:
        rodizio = _RODIZIO_COM_VAGA if com_vaga else _RODIZIO_SEM_VAGA
        return rodizio[(self.tentativa - 1) % len(rodizio)]


T = TypeVar("T")


@dataclass(frozen=True)
class SugestaoRefinada(Generic[T]):
    """O que a IA sugeriu e o foco usado, para a tela mostrar ao usuário."""

    valor: T
    foco: FocoRefino
