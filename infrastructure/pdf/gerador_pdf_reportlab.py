"""Adapter (implementa GeradorPdfPort) que gera o PDF final do currículo com ReportLab.

O layout segue o modelo de referência observado: cabeçalho com nome em
destaque e contatos, seções com título em negrito e linha divisória, e corpo
em parágrafos/bullets conforme o conteúdo de cada seção.
"""
from __future__ import annotations

import io

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

from application.ports.gerador_pdf_port import GeradorPdfPort
from domain.curriculo import Curriculo, TipoSecao

_ORDEM_SECOES = (
    TipoSecao.TECNOLOGIAS,
    TipoSecao.PERFIL,
    TipoSecao.EXPERIENCIAS,
    TipoSecao.FORMACAO,
    TipoSecao.CERTIFICACOES,
    TipoSecao.IDIOMAS,
)


def _criar_estilos() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "nome": ParagraphStyle("Nome", parent=base["Title"], fontSize=18, alignment=0, spaceAfter=4),
        "contato": ParagraphStyle("Contato", parent=base["Normal"], fontSize=9, textColor="#333333"),
        "titulo_secao": ParagraphStyle(
            "TituloSecao",
            parent=base["Heading2"],
            fontSize=12,
            spaceBefore=10,
            spaceAfter=4,
        ),
        "corpo": ParagraphStyle("Corpo", parent=base["Normal"], fontSize=10, leading=14),
    }


class GeradorPdfReportLab(GeradorPdfPort):
    """Gera os bytes de um PDF a partir de um Curriculo, no layout padrão do sistema."""

    def gerar(self, curriculo: Curriculo) -> bytes:
        buffer = io.BytesIO()
        documento = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
            topMargin=1.5 * cm,
            bottomMargin=1.5 * cm,
        )
        estilos = _criar_estilos()

        elementos = []
        elementos.extend(self._montar_cabecalho(curriculo, estilos))
        elementos.extend(self._montar_secoes(curriculo, estilos))

        documento.build(elementos)
        return buffer.getvalue()

    def _montar_cabecalho(self, curriculo: Curriculo, estilos: dict) -> list:
        elementos = [Paragraph(curriculo.nome_completo, estilos["nome"])]

        linha_contato_partes = []
        if curriculo.linkedin:
            linha_contato_partes.append(f"LinkedIn: {curriculo.linkedin}")
        if curriculo.email:
            linha_contato_partes.append(f"Email: {curriculo.email}")
        if linha_contato_partes:
            elementos.append(Paragraph(" | ".join(linha_contato_partes), estilos["contato"]))

        elementos.append(Spacer(1, 8))
        elementos.append(HRFlowable(width="100%", thickness=1, color="#000000"))
        return elementos

    def _montar_secoes(self, curriculo: Curriculo, estilos: dict) -> list:
        elementos = []
        for tipo in _ORDEM_SECOES:
            secao = curriculo.obter_secao(tipo)
            if secao is None:
                continue
            elementos.append(Paragraph(secao.titulo, estilos["titulo_secao"]))
            elementos.append(HRFlowable(width="100%", thickness=0.5, color="#666666"))
            elementos.append(Spacer(1, 4))
            elementos.extend(self._formatar_conteudo(secao.conteudo, estilos["corpo"]))
        return elementos

    @staticmethod
    def _formatar_conteudo(conteudo: str, estilo_corpo: ParagraphStyle) -> list:
        """Converte o texto em parágrafos, tratando linhas iniciadas com marcador como bullets."""
        elementos = []
        for linha in conteudo.split("\n"):
            linha_tratada = linha.strip()
            if not linha_tratada:
                continue
            if linha_tratada.startswith(("-", "•", "*")):
                texto = linha_tratada.lstrip("-•* ").strip()
                elementos.append(Paragraph(f"&bull;&nbsp;&nbsp;{texto}", estilo_corpo))
            else:
                elementos.append(Paragraph(linha_tratada, estilo_corpo))
            elementos.append(Spacer(1, 2))
        return elementos
