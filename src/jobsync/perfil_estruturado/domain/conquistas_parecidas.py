"""Regra de similaridade textual entre conquistas de uma experiência (JOB-0042).

Compara o texto normalizado (minúsculas, sem acento e sem pontuação) pela
sobreposição das palavras relevantes. É determinística e não usa IA: pode deixar
passar paráfrases distantes, e o aviso de duplicidade é só informativo.
"""
from __future__ import annotations

import re
import unicodedata

LIMITE_DE_SIMILARIDADE = 0.6
TAMANHO_MINIMO_DA_PALAVRA = 3

_NAO_ALFANUMERICO = re.compile(r"[^a-z0-9]+")


def normalizar_texto(texto: str) -> str:
    """Minúsculas, sem acento e sem pontuação, com espaços simples."""
    sem_acento = unicodedata.normalize("NFKD", texto.lower()).encode("ascii", "ignore").decode("ascii")
    return _NAO_ALFANUMERICO.sub(" ", sem_acento).strip()


def _palavras_relevantes(texto_normalizado: str) -> frozenset[str]:
    return frozenset(
        palavra for palavra in texto_normalizado.split() if len(palavra) >= TAMANHO_MINIMO_DA_PALAVRA
    )


def sao_parecidas(texto_a: str, texto_b: str) -> bool:
    """Indica se dois textos de conquista dizem praticamente a mesma coisa."""
    normalizado_a = normalizar_texto(texto_a)
    normalizado_b = normalizar_texto(texto_b)
    if normalizado_a and normalizado_a == normalizado_b:
        return True

    palavras_a = _palavras_relevantes(normalizado_a)
    palavras_b = _palavras_relevantes(normalizado_b)
    uniao = palavras_a | palavras_b
    if not uniao:
        return False
    return len(palavras_a & palavras_b) / len(uniao) >= LIMITE_DE_SIMILARIDADE
