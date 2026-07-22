"""Adapter responsável por extrair o texto bruto (não estruturado) de um PDF.

Usa pdfplumber, biblioteca madura e amplamente utilizada para extração de
texto preservando a ordem de leitura do documento.
"""
from __future__ import annotations

import io

import pdfplumber


class ExtratorTextoPdfPlumber:
    """Extrai texto bruto de um PDF a partir de seus bytes."""

    def extrair_texto(self, conteudo_pdf: bytes) -> str:
        if not conteudo_pdf:
            raise ValueError("O conteúdo do PDF está vazio.")

        partes_texto: list[str] = []
        with pdfplumber.open(io.BytesIO(conteudo_pdf)) as pdf:
            if len(pdf.pages) == 0:
                raise ValueError("O PDF não contém páginas.")
            for pagina in pdf.pages:
                texto_pagina = pagina.extract_text() or ""
                partes_texto.append(texto_pagina)

        texto_completo = "\n".join(partes_texto).strip()
        if not texto_completo:
            raise ValueError(
                "Não foi possível extrair texto do PDF. "
                "Verifique se o arquivo não é uma imagem escaneada sem OCR."
            )
        return texto_completo
