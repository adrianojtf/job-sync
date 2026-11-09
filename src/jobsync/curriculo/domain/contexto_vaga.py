"""Value Object: contexto da vaga-alvo usado para ajustar um trecho do currículo.

Agrupa o que as portas de ajuste precisam saber da vaga, para que os casos de
uso de sugestão recebam um único parâmetro, presente ou ausente.
"""
from __future__ import annotations

from dataclasses import dataclass

from jobsync.vaga.domain.analise_vaga import AnaliseVaga

IDIOMAS_ALVO_SUPORTADOS = ("pt", "en")


@dataclass(frozen=True)
class ContextoVaga:
    """Descrição, idioma alvo, análise estruturada e cargo-alvo (título) da vaga."""

    descricao_vaga: str
    idioma_alvo: str
    analise_vaga: AnaliseVaga
    cargo_alvo: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "cargo_alvo", (self.cargo_alvo or "").strip())
        if not self.descricao_vaga or not self.descricao_vaga.strip():
            raise ValueError("A descrição da vaga é obrigatória.")
        if self.idioma_alvo not in IDIOMAS_ALVO_SUPORTADOS:
            raise ValueError(
                f"idioma alvo inválido: '{self.idioma_alvo}'. "
                f"Idiomas suportados: {sorted(IDIOMAS_ALVO_SUPORTADOS)}"
            )
