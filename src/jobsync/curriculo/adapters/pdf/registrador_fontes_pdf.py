"""Registro da família tipográfica do PDF de currículo no ReportLab."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

logger = logging.getLogger(__name__)

_DIRETORIO_PADRAO = Path(__file__).parent / "fontes"
_NOME_FAMILIA = "Carlito"
_ARQUIVOS = {
    "regular": "Carlito-Regular.ttf",
    "bold": "Carlito-Bold.ttf",
    "italic": "Carlito-Italic.ttf",
    "bold_italic": "Carlito-BoldItalic.ttf",
}


@dataclass(frozen=True)
class FamiliaFonte:
    """Nomes efetivos das variações de fonte registradas no ReportLab."""

    regular: str
    bold: str
    italic: str
    bold_italic: str


_FAMILIA_CARLITO = FamiliaFonte(
    regular=_NOME_FAMILIA,
    bold=f"{_NOME_FAMILIA}-Bold",
    italic=f"{_NOME_FAMILIA}-Italic",
    bold_italic=f"{_NOME_FAMILIA}-BoldItalic",
)

_FAMILIA_HELVETICA = FamiliaFonte(
    regular="Helvetica",
    bold="Helvetica-Bold",
    italic="Helvetica-Oblique",
    bold_italic="Helvetica-BoldOblique",
)


class RegistradorFontesPdf:
    """Registra a Carlito uma única vez; sem os arquivos, usa Helvetica."""

    def __init__(self, diretorio_fontes: Path | None = None) -> None:
        self._diretorio_fontes = diretorio_fontes or _DIRETORIO_PADRAO

    def registrar(self) -> FamiliaFonte:
        caminhos = {variacao: self._diretorio_fontes / arquivo for variacao, arquivo in _ARQUIVOS.items()}
        if not all(caminho.is_file() for caminho in caminhos.values()):
            logger.warning(
                "Fonte Carlito não encontrada em %s; usando Helvetica", self._diretorio_fontes
            )
            return _FAMILIA_HELVETICA

        if _FAMILIA_CARLITO.regular not in pdfmetrics.getRegisteredFontNames():
            self._registrar_carlito(caminhos)
        return _FAMILIA_CARLITO

    @staticmethod
    def _registrar_carlito(caminhos: dict[str, Path]) -> None:
        for variacao, caminho in caminhos.items():
            pdfmetrics.registerFont(TTFont(getattr(_FAMILIA_CARLITO, variacao), str(caminho)))
        pdfmetrics.registerFontFamily(
            _FAMILIA_CARLITO.regular,
            normal=_FAMILIA_CARLITO.regular,
            bold=_FAMILIA_CARLITO.bold,
            italic=_FAMILIA_CARLITO.italic,
            boldItalic=_FAMILIA_CARLITO.bold_italic,
        )
