"""Lacunas entre a vaga e o histórico do candidato (JOB-0043).

Uma lacuna é um tema central da vaga que o histórico não sustenta. Vira uma pergunta ao candidato:
se ele viveu aquilo, a resposta se torna uma conquista do banco; se não, o tema fica de fora.
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from jobsync.curriculo.domain.avaliacao_experiencia import ExperienciaParaAvaliacao
from jobsync.shared_kernel.domain.texto_normalizado import normalizar_texto

LIMITE_DE_LACUNAS = 5


@dataclass(frozen=True)
class LacunaDaVaga:
    """Tema da vaga sem sustentação no histórico e a pergunta que o candidato responde."""

    tema: str
    pergunta: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "tema", (self.tema or "").strip())
        object.__setattr__(self, "pergunta", (self.pergunta or "").strip())
        if not self.tema:
            raise ValueError("O tema da lacuna não pode ser vazio.")
        if not self.pergunta:
            raise ValueError("A pergunta da lacuna não pode ser vazia.")


@dataclass(frozen=True)
class HistoricoDoCandidato:
    """O que o candidato já mostra: resumo, experiências (com o banco de conquistas) e tecnologias."""

    resumo: str
    experiencias: tuple[ExperienciaParaAvaliacao, ...]
    tecnologias: tuple[str, ...]

    def sem_experiencias(self) -> bool:
        return not self.experiencias


def principais(lacunas: Sequence[LacunaDaVaga], limite: int = LIMITE_DE_LACUNAS) -> tuple[LacunaDaVaga, ...]:
    """Mantém a ordem, remove tema repetido e corta no limite, sem depender de a IA obedecer."""
    vistos: set[str] = set()
    resultado: list[LacunaDaVaga] = []
    for lacuna in lacunas:
        chave = normalizar_texto(lacuna.tema)
        if chave in vistos:
            continue
        vistos.add(chave)
        resultado.append(lacuna)
        if len(resultado) >= limite:
            break
    return tuple(resultado)
