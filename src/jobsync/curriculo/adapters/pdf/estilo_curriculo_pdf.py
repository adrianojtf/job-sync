"""Tokens visuais do PDF de currículo, medidos no modelo de referência do JOB-0016."""
from __future__ import annotations

from dataclasses import dataclass

from reportlab.lib.colors import Color, HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle

from jobsync.curriculo.adapters.pdf.registrador_fontes_pdf import FamiliaFonte

_PRETO = HexColor("#000000")
_AZUL_MARINHO = HexColor("#1F3864")
_CINZA = HexColor("#595959")
_AZUL_LINK = HexColor("#0563C1")
_TAMANHO_CORPO = 10.5
_ENTRELINHA_CORPO = 12.8


@dataclass(frozen=True)
class EstiloCurriculoPdf:
    """Cores, medidas de página e estilos de parágrafo do layout do currículo."""

    familia: FamiliaFonte
    margem_lateral: float = 45
    cor_destaque: Color = _AZUL_MARINHO
    cor_secundaria: Color = _CINZA
    cor_link: Color = _AZUL_LINK
    espessura_linha_secao: float = 0.75
    recuo_direito_periodo: float = 54
    largura_periodo: float = 140
    espaco_antes_da_empresa: float = 10

    @property
    def nome(self) -> ParagraphStyle:
        return ParagraphStyle(
            "Nome", fontName=self.familia.bold, fontSize=16, leading=19,
            alignment=TA_CENTER, textColor=self.cor_destaque, spaceAfter=3,
        )

    @property
    def contato(self) -> ParagraphStyle:
        return ParagraphStyle(
            "Contato", fontName=self.familia.regular, fontSize=10, leading=12,
            alignment=TA_CENTER, textColor=self.cor_secundaria,
        )

    @property
    def titulo_secao(self) -> ParagraphStyle:
        return ParagraphStyle(
            "TituloSecao", fontName=self.familia.bold, fontSize=11, leading=13,
            alignment=TA_LEFT, textColor=self.cor_destaque, spaceBefore=15, spaceAfter=2, keepWithNext=1,
        )

    @property
    def corpo(self) -> ParagraphStyle:
        return ParagraphStyle(
            "Corpo", fontName=self.familia.regular, fontSize=_TAMANHO_CORPO,
            leading=_ENTRELINHA_CORPO, textColor=_PRETO,
        )

    @property
    def perfil(self) -> ParagraphStyle:
        return ParagraphStyle("Perfil", parent=self.corpo, spaceAfter=4)

    @property
    def tecnologia(self) -> ParagraphStyle:
        return ParagraphStyle("Tecnologia", parent=self.corpo, spaceAfter=2)

    @property
    def empresa(self) -> ParagraphStyle:
        return ParagraphStyle(
            "Empresa", fontName=self.familia.bold, fontSize=11.5, leading=14, textColor=_PRETO, keepWithNext=1,
            spaceBefore=self.espaco_antes_da_empresa,
        )

    @property
    def periodo(self) -> ParagraphStyle:
        return ParagraphStyle(
            "Periodo", fontName=self.familia.regular, fontSize=_TAMANHO_CORPO, leading=14,
            alignment=TA_RIGHT, textColor=self.cor_secundaria,
        )

    @property
    def cargo(self) -> ParagraphStyle:
        return ParagraphStyle(
            "Cargo", fontName=self.familia.italic, fontSize=_TAMANHO_CORPO,
            leading=_ENTRELINHA_CORPO, textColor=self.cor_destaque, spaceAfter=4, keepWithNext=1,
        )

    @property
    def topico(self) -> ParagraphStyle:
        return ParagraphStyle(
            "Topico", parent=self.corpo, leftIndent=36, bulletIndent=18,
            bulletFontName=self.familia.regular, bulletFontSize=10, spaceAfter=3,
        )

    @property
    def contexto(self) -> ParagraphStyle:
        return ParagraphStyle(
            "Contexto", fontName=self.familia.italic, fontSize=_TAMANHO_CORPO,
            leading=_ENTRELINHA_CORPO, textColor=self.cor_secundaria, spaceBefore=2,
        )
