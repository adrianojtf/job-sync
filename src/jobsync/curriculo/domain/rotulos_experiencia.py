"""Rótulos da linha de contexto de uma experiência no texto do currículo.

O `Curriculo` e o gerador de PDF trabalham com texto. A linha final de cada experiência,
"Contexto: ..." ou "Context: ...", é a convenção que o gerador reconhece para desenhá-la
em itálico cinza.
"""
from __future__ import annotations

ROTULO_CONTEXTO = {"pt": "Contexto", "en": "Context"}

ROTULOS_CONTEXTO_RECONHECIDOS = frozenset(rotulo.lower() for rotulo in ROTULO_CONTEXTO.values())


def rotulo_contexto(idioma_alvo: str) -> str:
    """Rótulo do contexto no idioma alvo; levanta ValueError se o idioma não for suportado."""
    try:
        return ROTULO_CONTEXTO[idioma_alvo]
    except KeyError:
        raise ValueError(
            f"idioma alvo inválido: '{idioma_alvo}'. "
            f"Idiomas suportados: {sorted(ROTULO_CONTEXTO)}"
        ) from None
