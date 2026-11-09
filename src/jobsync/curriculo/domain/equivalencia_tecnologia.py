"""Value Objects: equivalência entre tecnologias do perfil e da vaga, e onde ela é aplicada.

Uma equivalência diz que uma tecnologia do perfil (`original`) pode aparecer no currículo
como a tecnologia pedida pela vaga (`alvo`), por serem da mesma categoria (ex.: React e
Angular). Quem decide em quais experiências a troca acontece é o `PlanoAdaptacao`.
"""
from __future__ import annotations

import re
from dataclasses import dataclass


def _normalizar(nome: str) -> str:
    return (nome or "").strip()


def menciona_tecnologia(texto: str, tecnologia: str) -> bool:
    """Indica se o texto cita a tecnologia como palavra inteira, sem diferenciar maiúsculas.

    "Java" não casa com "JavaScript"; nomes com símbolos (".NET", "C#", "Node.js") são aceitos.
    """
    padrao = rf"(?<!\w){re.escape(tecnologia)}(?!\w)"
    return re.search(padrao, texto, flags=re.IGNORECASE) is not None


@dataclass(frozen=True)
class EquivalenciaTecnologia:
    original: str
    alvo: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "original", _normalizar(self.original))
        object.__setattr__(self, "alvo", _normalizar(self.alvo))
        if not self.original or not self.alvo:
            raise ValueError("Informe a tecnologia original e a tecnologia alvo da equivalência.")
        if self.original.casefold() == self.alvo.casefold():
            raise ValueError("A tecnologia original e a alvo precisam ser diferentes.")


@dataclass(frozen=True)
class AjusteTecnologia:
    """Troca de `equivalencia.original` por `equivalencia.alvo` em uma experiência."""

    indice_experiencia: int
    equivalencia: EquivalenciaTecnologia


@dataclass(frozen=True)
class ManutencaoTecnologia:
    """Experiência que mantém a tecnologia original e deve citá-la de forma explícita."""

    indice_experiencia: int
    tecnologia: str


@dataclass(frozen=True)
class DiretrizesExperiencia:
    """O que a IA deve trocar e o que deve manter explícito em uma experiência."""

    trocar: tuple[EquivalenciaTecnologia, ...] = ()
    manter: tuple[str, ...] = ()
