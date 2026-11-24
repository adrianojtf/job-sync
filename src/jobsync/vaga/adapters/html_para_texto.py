"""Conversão de HTML de vaga em texto, preservando parágrafos e listas."""
from __future__ import annotations

import re
from typing import Sequence

from bs4 import BeautifulSoup

_TAGS_DE_BLOCO = ("p", "div", "section", "article", "blockquote", "table", "tr", "h1", "h2", "h3", "h4", "h5", "h6")
_ESPACOS = re.compile(r"[ \t\xa0]+")
_LINHAS_EM_BRANCO = re.compile(r"\n{3,}")


def converter_html_em_texto(html: str, ignorar_tags: Sequence[str] = ()) -> str:
    """Converte HTML em texto simples: `<br>` vira quebra de linha, blocos viram parágrafos e `<li>` vira "- item"."""
    if not html or not html.strip():
        return ""

    sopa = BeautifulSoup(html, "html.parser")
    for tag in sopa(["script", "style", *ignorar_tags]):
        tag.decompose()
    for quebra in sopa.find_all("br"):
        quebra.replace_with("\n")
    for item in sopa.find_all("li"):
        item.insert_before("\n- ")
    for lista in sopa.find_all(["ul", "ol"]):
        lista.insert_after("\n")
    for bloco in sopa.find_all(_TAGS_DE_BLOCO):
        bloco.insert_before("\n\n")
        bloco.insert_after("\n\n")

    linhas = [_ESPACOS.sub(" ", linha).strip() for linha in sopa.get_text().splitlines()]
    return _LINHAS_EM_BRANCO.sub("\n\n", "\n".join(linhas)).strip()
