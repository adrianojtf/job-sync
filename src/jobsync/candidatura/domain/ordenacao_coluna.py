"""Regra de ordenação dos cartões dentro de uma coluna do Kanban."""
from __future__ import annotations


def reposicionar(ids: tuple[str, ...], movido_id: str, posicao: int | None) -> tuple[str, ...]:
    """Devolve a nova ordem da coluna com `movido_id` na `posicao` informada.

    `None` coloca o cartão no topo e uma posição acima do tamanho da coluna o coloca no fim.
    Se `movido_id` já estiver em `ids`, ele é removido antes de ser reinserido.
    """
    if posicao is not None and posicao < 0:
        raise ValueError("A posição não pode ser negativa.")
    restantes = tuple(id_ for id_ in ids if id_ != movido_id)
    indice = 0 if posicao is None else min(posicao, len(restantes))
    return restantes[:indice] + (movido_id,) + restantes[indice:]
