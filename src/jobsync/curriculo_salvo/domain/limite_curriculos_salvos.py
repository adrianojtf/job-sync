"""Regra de negócio: limite de currículos salvos na biblioteca de cada perfil."""
from __future__ import annotations

LIMITE_CURRICULOS_POR_PERFIL = 10


class LimiteCurriculosSalvosExcedido(ValueError):
    """Levantado quando o perfil já atingiu o limite de currículos salvos."""


def garantir_espaco(quantidade_atual: int) -> None:
    """Levanta LimiteCurriculosSalvosExcedido se a biblioteca não comporta mais um currículo."""
    if quantidade_atual >= LIMITE_CURRICULOS_POR_PERFIL:
        raise LimiteCurriculosSalvosExcedido(
            f"Limite de {LIMITE_CURRICULOS_POR_PERFIL} currículos salvos atingido. "
            "Remova um currículo existente antes de salvar um novo."
        )
