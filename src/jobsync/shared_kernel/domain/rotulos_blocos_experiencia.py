"""Rótulos dos quatro blocos de uma experiência: contexto, responsabilidades, realizações e skills.

É a fonte única dos rótulos usados pelo texto do currículo, pelo gerador de PDF e pelo
reconhecimento de blocos no currículo inicial. Cada bloco tem um rótulo por idioma e apelidos
reconhecidos na leitura (ex.: "Key Achievements", "Principais entregas").
"""
from __future__ import annotations

from enum import Enum, auto

from jobsync.shared_kernel.domain.texto_normalizado import normalizar_texto


class BlocoExperiencia(Enum):
    CONTEXTO = auto()
    RESPONSABILIDADES = auto()
    REALIZACOES = auto()
    SKILLS = auto()


_ROTULOS: dict[BlocoExperiencia, dict[str, str]] = {
    BlocoExperiencia.CONTEXTO: {"pt": "Contexto", "en": "Context"},
    BlocoExperiencia.RESPONSABILIDADES: {
        "pt": "Principais responsabilidades",
        "en": "Key Responsibilities",
    },
    BlocoExperiencia.REALIZACOES: {"pt": "Principais realizações", "en": "Key Achievements"},
    BlocoExperiencia.SKILLS: {"pt": "Tecnologias", "en": "Technologies"},
}

_APELIDOS: dict[BlocoExperiencia, tuple[str, ...]] = {
    BlocoExperiencia.CONTEXTO: (),
    BlocoExperiencia.RESPONSABILIDADES: ("Responsibilities", "Responsabilidades", "Atribuições"),
    BlocoExperiencia.REALIZACOES: (
        "Achievements",
        "Realizações",
        "Conquistas",
        "Principais conquistas",
        "Principais entregas",
        "Entregas",
    ),
    BlocoExperiencia.SKILLS: ("Skills", "Key Skills", "Tech Stack", "Habilidades"),
}

_RECONHECIDOS: dict[str, BlocoExperiencia] = {
    normalizar_texto(texto): bloco
    for bloco in BlocoExperiencia
    for texto in (*_ROTULOS[bloco].values(), *_APELIDOS[bloco])
}

IDIOMAS_SUPORTADOS = ("en", "pt")


def rotulo_do_bloco(bloco: BlocoExperiencia, idioma_alvo: str) -> str:
    """Rótulo do bloco no idioma alvo; levanta ValueError se o idioma não for suportado."""
    try:
        return _ROTULOS[bloco][idioma_alvo]
    except KeyError:
        raise ValueError(
            f"idioma alvo inválido: '{idioma_alvo}'. Idiomas suportados: {list(IDIOMAS_SUPORTADOS)}"
        ) from None


def bloco_do_rotulo(texto: str) -> BlocoExperiencia | None:
    """Bloco que o texto nomeia (rótulo ou apelido, sem caixa, acento ou pontuação), ou None."""
    return _RECONHECIDOS.get(normalizar_texto(texto))
