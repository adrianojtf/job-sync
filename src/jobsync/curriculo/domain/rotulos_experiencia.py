"""Rótulos da linha de contexto de uma experiência no texto do currículo.

O `Curriculo` e o gerador de PDF trabalham com texto. A linha de contexto de cada experiência,
"Contexto: ..." ou "Context: ...", é a convenção que o gerador reconhece para desenhá-la
em itálico cinza. Os rótulos vêm de `shared_kernel`, a fonte única dos quatro blocos.
"""
from __future__ import annotations

from jobsync.shared_kernel.domain.rotulos_blocos_experiencia import (
    IDIOMAS_SUPORTADOS,
    BlocoExperiencia,
    bloco_do_rotulo,
    rotulo_do_bloco,
)

ROTULO_CONTEXTO = {idioma: rotulo_do_bloco(BlocoExperiencia.CONTEXTO, idioma) for idioma in IDIOMAS_SUPORTADOS}

ROTULOS_CONTEXTO_RECONHECIDOS = frozenset(rotulo.lower() for rotulo in ROTULO_CONTEXTO.values())


def rotulo_contexto(idioma_alvo: str) -> str:
    """Rótulo do contexto no idioma alvo; levanta ValueError se o idioma não for suportado."""
    return rotulo_do_bloco(BlocoExperiencia.CONTEXTO, idioma_alvo)


__all__ = ["ROTULO_CONTEXTO", "ROTULOS_CONTEXTO_RECONHECIDOS", "bloco_do_rotulo", "rotulo_contexto"]
