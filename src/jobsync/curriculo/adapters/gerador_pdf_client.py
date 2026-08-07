"""Adapter (implementa GeradorPdfPort) que gera o PDF final do currículo com ReportLab.

O layout segue o modelo de referência observado: cabeçalho com nome em
destaque e contatos, seções com título em negrito e linha divisória, e corpo
em parágrafos/bullets conforme o conteúdo de cada seção.
"""
from __future__ import annotations

import io
import re

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

from jobsync.curriculo import Curriculo, TipoSecao
from jobsync.curriculo.domain.gerador_pdf_port import GeradorPdfPort
from jobsync.shared_kernel.domain import CatalogoLocalizacao

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


class GeradorPdfClient(GeradorPdfPort):
    """Gera os bytes de um PDF a partir de um Curriculo, no layout padrão do sistema."""

    def __init__(self, catalogo: CatalogoLocalizacao | None = None) -> None:
        self._catalogo = catalogo or CatalogoLocalizacao()

    def gerar(self, curriculo: Curriculo, idioma_alvo: str) -> bytes:
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
        elementos.extend(self._montar_secoes(curriculo, estilos, idioma_alvo))

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

    def _montar_secoes(self, curriculo: Curriculo, estilos: dict, idioma_alvo: str) -> list:
        elementos = []
        for tipo in _ORDEM_SECOES:
            secao = curriculo.obter_secao(tipo)
            if secao is None:
                continue
            titulo_localizado = self._obter_titulo_secao(tipo, secao.titulo, idioma_alvo)
            elementos.append(Paragraph(titulo_localizado, estilos["titulo_secao"]))
            elementos.append(HRFlowable(width="100%", thickness=0.5, color="#666666"))
            elementos.append(Spacer(1, 4))
            elementos.extend(self._formatar_conteudo(secao.conteudo, estilos["corpo"], tipo, idioma_alvo))
        return elementos

    def _obter_titulo_secao(self, tipo_secao: TipoSecao, titulo_original: str, idioma_alvo: str) -> str:
        chave = {
            TipoSecao.TECNOLOGIAS: "tecnologias",
            TipoSecao.PERFIL: "perfil",
            TipoSecao.EXPERIENCIAS: "experiencias",
            TipoSecao.FORMACAO: "formacao",
            TipoSecao.CERTIFICACOES: "certificacoes",
            TipoSecao.IDIOMAS: "idiomas",
        }.get(tipo_secao)
        if chave is None:
            return titulo_original
        return self._catalogo.localizar_secao(idioma_alvo, chave, fallback=titulo_original)

    @staticmethod
    def _escape_text(conteudo: str) -> str:
        return (
            conteudo.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

    @staticmethod
    def _aplicar_enfase(conteudo: str, tipo_secao: TipoSecao, idioma_alvo: str = "en", catalogo: CatalogoLocalizacao | None = None) -> str:
        conteudo = GeradorPdfClient._escape_text(conteudo)
        if tipo_secao == TipoSecao.TECNOLOGIAS:
            return GeradorPdfClient._negritar_categorias_tecnologia(conteudo, idioma_alvo, catalogo)
        if tipo_secao == TipoSecao.EXPERIENCIAS:
            return conteudo
        if tipo_secao == TipoSecao.FORMACAO:
            return GeradorPdfClient._negritar_formacao(conteudo)
        return conteudo

    @staticmethod
    def _traduzir_categorias_tecnologia(conteudo: str, idioma_alvo: str, catalogo: CatalogoLocalizacao | None = None) -> str:
        catalogo = catalogo or CatalogoLocalizacao()
        linhas = []
        for linha in conteudo.splitlines():
            if not linha.strip():
                linhas.append(linha)
                continue
            correspondencia = re.match(r"^(?P<prefixo>(?:[-•*]\s*)?)(?P<label>[^:]+?)(?P<separador>\s*:\s*)(?P<rest>.*)$", linha)
            if not correspondencia:
                linhas.append(linha)
                continue
            label = correspondencia.group("label").strip()
            label_localizado = catalogo.localizar_categoria(idioma_alvo, label)
            linhas.append(
                f"{correspondencia.group('prefixo')}{label_localizado}{correspondencia.group('separador')}{correspondencia.group('rest')}"
            )
        return "\n".join(linhas)

    @staticmethod
    def _negritar_categorias_tecnologia(
        conteudo: str,
        idioma_alvo: str = "en",
        catalogo: CatalogoLocalizacao | None = None,
    ) -> str:
        catalogo = catalogo or CatalogoLocalizacao()
        texto_localizado = GeradorPdfClient._traduzir_categorias_tecnologia(conteudo, idioma_alvo, catalogo)
        idioma_normalizado = catalogo.normalizar_idioma(idioma_alvo)
        categorias = [
            mapeamento[idioma_normalizado] if idioma_normalizado in mapeamento else mapeamento["pt"]
            for mapeamento in catalogo.categorias_tecnologia.values()
        ]
        padrao = re.compile(rf"(?P<prefixo>^|[-•*]\s*)(?P<label>{'|'.join(re.escape(c) for c in categorias)})(?P<separador>\s*:)", re.MULTILINE)
        return padrao.sub(lambda m: f"{m.group('prefixo')}<b>{m.group('label')}</b>{m.group('separador')}", texto_localizado)

    @staticmethod
    def _negritar_experiencia(conteudo: str) -> str:
        return f"<b>{GeradorPdfClient._escape_text(conteudo)}</b>"

    @staticmethod
    def _negritar_formacao(conteudo: str) -> str:
        def formatar_linha(linha: str) -> str:
            prefixo, texto = GeradorPdfClient._separar_rotulo_formacao(linha)
            if ";" in texto:
                partes = [parte.strip() for parte in texto.split(";")]
                texto_formatado = "; ".join(GeradorPdfClient._formatar_bloco_formacao(parte) for parte in partes)
            else:
                texto_formatado = GeradorPdfClient._formatar_bloco_formacao(texto)
            return f"{prefixo}{texto_formatado}"

        linhas = conteudo.split("\n")
        return "\n".join(formatar_linha(linha) for linha in linhas)

    @staticmethod
    def _separar_rotulo_formacao(conteudo: str) -> tuple[str, str]:
        padrao = re.compile(
            r"^(?P<label>Languages|Frameworks|Web Development|DevOps|Databases|Version Control|Other|Education|Educação|Formação|Academic)\s*:\s*(?P<rest>.*)$",
            re.IGNORECASE,
        )
        correspondencia = padrao.match(conteudo)
        if not correspondencia:
            return "", conteudo
        return f"<b>{correspondencia.group('label').strip()}</b>: ", correspondencia.group("rest")

    @staticmethod
    def _formatar_bloco_formacao(conteudo: str) -> str:
        texto = conteudo.strip()
        if " - " in texto:
            nome, resto = texto.split(" - ", 1)
            if "," in nome:
                primeiro, complemento = nome.split(",", 1)
                nome_formatado = f"<b>{primeiro.strip()}</b>, {complemento.strip()}"
            else:
                nome_formatado = GeradorPdfClient._negritar_instituicao_ou_titulo(nome)

            resto_bruto = resto.strip()
            resto_formatado = GeradorPdfClient._negritar_grau_formacao(resto_bruto)
            if resto_formatado == resto_bruto:
                resto_formatado = GeradorPdfClient._negritar_instituicao_ou_titulo(resto_bruto)
            return f"{nome_formatado} - {resto_formatado}"
        if "," in texto:
            primeiro, resto = texto.split(",", 1)
            primeiro_formatado = GeradorPdfClient._negritar_instituicao_ou_titulo(primeiro)
            resto_formatado = GeradorPdfClient._negritar_grau_formacao(resto)
            return f"{primeiro_formatado}, {resto_formatado.lstrip()}"
        return GeradorPdfClient._negritar_grau_formacao(texto)

    @staticmethod
    def _negritar_instituicao_ou_titulo(texto: str) -> str:
        texto = texto.strip()
        if not texto:
            return texto
        if texto.startswith("<b>") and texto.endswith("</b>"):
            return texto
        return f"<b>{texto}</b>"

    @staticmethod
    def _negritar_grau_formacao(conteudo: str) -> str:
        padrao = re.compile(
            r"(?P<grau>\b(?:Associate Degree|Bachelor(?:'s)? Degree|Master(?:'s)? Degree|Technical Degree|Diploma|Certificate|Certification|Technical Diploma|Técnico|Bacharelado|Mestrado|Graduação)(?:\s+in\b[^,;]*)?)",
            re.IGNORECASE,
        )

        def substituir(m: re.Match[str]) -> str:
            grau = m.group("grau").strip()
            if grau.startswith("<b>") and grau.endswith("</b>"):
                return grau
            return f"<b>{grau}</b>"

        return padrao.sub(substituir, conteudo)

    def _formatar_conteudo(
        self,
        conteudo: str,
        estilo_corpo: ParagraphStyle,
        tipo_secao: TipoSecao,
        idioma_alvo: str = "en",
    ) -> list:
        """Converte o texto em parágrafos, tratando linhas iniciadas com marcador como bullets."""
        if tipo_secao == TipoSecao.EXPERIENCIAS:
            return self._formatar_conteudo_experiencias(conteudo, estilo_corpo)
        if tipo_secao == TipoSecao.TECNOLOGIAS:
            return self._formatar_conteudo_tecnologias(conteudo, estilo_corpo, idioma_alvo)

        elementos = []
        for linha in conteudo.split("\n"):
            linha_tratada = linha.strip()
            if not linha_tratada:
                continue
            if linha_tratada.startswith(("-", "•", "*")):
                texto = linha_tratada.lstrip("-•* ").strip()
                elementos.append(
                    Paragraph(f"&bull;&nbsp;&nbsp;{self._aplicar_enfase(texto, tipo_secao, idioma_alvo, self._catalogo)}", estilo_corpo)
                )
            else:
                elementos.append(Paragraph(self._aplicar_enfase(linha_tratada, tipo_secao, idioma_alvo, self._catalogo), estilo_corpo))
            elementos.append(Spacer(1, 2))
        return elementos

    def _formatar_conteudo_tecnologias(
        self,
        conteudo: str,
        estilo_corpo: ParagraphStyle,
        idioma_alvo: str = "en",
    ) -> list:
        linhas = [linha.strip() for linha in conteudo.split("\n") if linha.strip()]
        elementos = []

        for indice, linha in enumerate(linhas):
            linha_tratada = linha.strip()
            if linha_tratada.startswith(("-", "•", "*")):
                texto = linha_tratada.lstrip("-•* ").strip()
                texto_formatado = self._aplicar_enfase(texto, TipoSecao.TECNOLOGIAS, idioma_alvo, self._catalogo)
                elementos.append(Paragraph(f"&bull;&nbsp;&nbsp;{texto_formatado}", estilo_corpo))
            else:
                texto_formatado = self._aplicar_enfase(linha_tratada, TipoSecao.TECNOLOGIAS, idioma_alvo, self._catalogo)
                elementos.append(Paragraph(texto_formatado, estilo_corpo))
            if indice < len(linhas) - 1:
                elementos.append(Spacer(1, 2))

        return elementos

    def _formatar_conteudo_experiencias(self, conteudo: str, estilo_corpo: ParagraphStyle) -> list:
        blocos = self._separar_blocos_experiencias(conteudo)
        elementos = []

        for indice_bloco, bloco in enumerate(blocos):
            for index, linha in enumerate(bloco):
                linha_tratada = linha.strip()
                if linha_tratada.startswith(("-", "•", "*")):
                    texto = linha_tratada.lstrip("-•* ").strip()
                    elementos.append(Paragraph(f"&bull;&nbsp;&nbsp;{self._escape_text(texto)}", estilo_corpo))
                    elementos.append(Spacer(1, 2))
                elif index == 0:
                    elementos.append(Paragraph(self._negritar_experiencia(linha_tratada), estilo_corpo))
                    elementos.append(Spacer(1, 2))
                elif index == 1 and self._parece_posicao_experiencia(linha_tratada):
                    elementos.append(Paragraph(self._negritar_experiencia(linha_tratada), estilo_corpo))
                    elementos.append(Spacer(1, 2))
                else:
                    elementos.append(Paragraph(self._escape_text(linha_tratada), estilo_corpo))
                    elementos.append(Spacer(1, 2))

            if indice_bloco < len(blocos) - 1:
                elementos.append(Spacer(1, 6))

        return elementos

    @staticmethod
    def _separar_blocos_experiencias(conteudo: str) -> list[list[str]]:
        blocos: list[list[str]] = []
        bloco_atual: list[str] = []

        for linha in conteudo.splitlines():
            linha_tratada = linha.strip()
            if not linha_tratada:
                if bloco_atual:
                    blocos.append(bloco_atual)
                    bloco_atual = []
                continue
            bloco_atual.append(linha_tratada)

        if bloco_atual:
            blocos.append(bloco_atual)

        return blocos

    @staticmethod
    def _parece_posicao_experiencia(linha: str) -> bool:
        if len(linha) > 80:
            return False
        if re.search(r"\d{4}", linha):
            return False
        return True
