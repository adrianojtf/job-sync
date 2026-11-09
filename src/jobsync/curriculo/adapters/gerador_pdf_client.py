"""Adapter (implementa GeradorPdfPort) que gera o PDF final do currículo com ReportLab.

O layout segue o modelo de referência do JOB-0016: cabeçalho centralizado com o nome em
caixa alta e o contato com link, seções com título em caixa alta e linha azul-marinho,
tecnologias uma categoria por linha e corpo em parágrafos conforme o conteúdo de cada seção.
Cores, tamanhos e fontes vêm de `EstiloCurriculoPdf`.
"""
from __future__ import annotations

import io
import re

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

from jobsync.curriculo import Curriculo, TipoSecao
from jobsync.curriculo.adapters.pdf.estilo_curriculo_pdf import EstiloCurriculoPdf
from jobsync.curriculo.adapters.pdf.registrador_fontes_pdf import RegistradorFontesPdf
from jobsync.curriculo.domain.gerador_pdf_port import GeradorPdfPort
from jobsync.curriculo.domain.rotulos_experiencia import ROTULOS_CONTEXTO_RECONHECIDOS
from jobsync.shared_kernel.domain import CatalogoLocalizacao

_ORDEM_SECOES = (
    TipoSecao.TECNOLOGIAS,
    TipoSecao.PERFIL,
    TipoSecao.EXPERIENCIAS,
    TipoSecao.FORMACAO,
    TipoSecao.CERTIFICACOES,
    TipoSecao.IDIOMAS,
)
_MARGEM_VERTICAL = 36
_FOLGA_LATERAL_DO_FRAME = 6  # padding interno do Frame do ReportLab, somado à margem do documento
_MARCADORES_DE_TOPICO = ("-", "•", "*")


class GeradorPdfClient(GeradorPdfPort):
    """Gera os bytes de um PDF a partir de um Curriculo, no layout padrão do sistema."""

    def __init__(
        self,
        catalogo: CatalogoLocalizacao | None = None,
        estilo: EstiloCurriculoPdf | None = None,
        registrador_fontes: RegistradorFontesPdf | None = None,
    ) -> None:
        self._catalogo = catalogo or CatalogoLocalizacao()
        self._estilo = estilo or EstiloCurriculoPdf(
            familia=(registrador_fontes or RegistradorFontesPdf()).registrar()
        )

    def gerar(self, curriculo: Curriculo, idioma_alvo: str) -> bytes:
        buffer = io.BytesIO()
        documento = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=self._estilo.margem_lateral - _FOLGA_LATERAL_DO_FRAME,
            rightMargin=self._estilo.margem_lateral - _FOLGA_LATERAL_DO_FRAME,
            topMargin=_MARGEM_VERTICAL,
            bottomMargin=_MARGEM_VERTICAL,
        )

        elementos = []
        elementos.extend(self._montar_cabecalho(curriculo))
        elementos.extend(self._montar_secoes(curriculo, idioma_alvo))

        documento.build(elementos)
        return buffer.getvalue()

    def _montar_cabecalho(self, curriculo: Curriculo) -> list:
        elementos = [Paragraph(self._escape_text(curriculo.nome_completo.upper()), self._estilo.nome)]

        partes_do_contato = []
        if curriculo.linkedin:
            partes_do_contato.append(f"LinkedIn: {self._link_do_linkedin(curriculo.linkedin)}")
        if curriculo.email:
            partes_do_contato.append(f"Email: {self._escape_text(curriculo.email)}")
        if partes_do_contato:
            elementos.append(Paragraph(" | ".join(partes_do_contato), self._estilo.contato))
        return elementos

    def _link_do_linkedin(self, linkedin: str) -> str:
        destino = linkedin if linkedin.startswith(("http://", "https://")) else f"https://{linkedin}"
        cor = "#" + self._estilo.cor_link.hexval()[2:]
        destino_escapado = self._escape_text(destino).replace('"', "&quot;")
        return f'<link href="{destino_escapado}" color="{cor}"><u>{self._escape_text(linkedin)}</u></link>'

    def _montar_secoes(self, curriculo: Curriculo, idioma_alvo: str) -> list:
        elementos = []
        for tipo in _ORDEM_SECOES:
            secao = curriculo.obter_secao(tipo)
            if secao is None:
                continue
            titulo_localizado = self._obter_titulo_secao(tipo, secao.titulo, idioma_alvo)
            cabecalho_da_secao = [
                Paragraph(self._escape_text(titulo_localizado.upper()), self._estilo.titulo_secao),
                self._linha_da_secao(),
            ]
            conteudo = self._formatar_conteudo(secao.conteudo, tipo, idioma_alvo)
            if conteudo:
                elementos.append(KeepTogether([*cabecalho_da_secao, conteudo[0]]))
                elementos.extend(conteudo[1:])
            else:
                elementos.extend(cabecalho_da_secao)
        return elementos

    def _linha_da_secao(self) -> HRFlowable:
        return HRFlowable(
            width="100%",
            thickness=self._estilo.espessura_linha_secao,
            color=self._estilo.cor_destaque,
            spaceBefore=2,
            spaceAfter=6,
        )

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
        return padrao.sub(lambda m: f"{m.group('prefixo')}<b>{m.group('label')}:</b>", texto_localizado)

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
        tipo_secao: TipoSecao,
        idioma_alvo: str = "en",
    ) -> list:
        """Converte o texto em parágrafos, tratando linhas iniciadas com marcador como bullets."""
        if tipo_secao == TipoSecao.EXPERIENCIAS:
            return self._formatar_conteudo_experiencias(conteudo)
        if tipo_secao == TipoSecao.TECNOLOGIAS:
            return self._formatar_conteudo_tecnologias(conteudo, idioma_alvo)
        if tipo_secao == TipoSecao.PERFIL:
            return self._formatar_conteudo_perfil(conteudo)

        elementos = []
        for linha in conteudo.split("\n"):
            linha_tratada = linha.strip()
            if not linha_tratada:
                continue
            if linha_tratada.startswith(_MARCADORES_DE_TOPICO):
                texto = linha_tratada.lstrip("-•* ").strip()
                elementos.append(
                    Paragraph(
                        f"&bull;&nbsp;&nbsp;{self._aplicar_enfase(texto, tipo_secao, idioma_alvo, self._catalogo)}",
                        self._estilo.corpo,
                    )
                )
            else:
                elementos.append(
                    Paragraph(
                        self._aplicar_enfase(linha_tratada, tipo_secao, idioma_alvo, self._catalogo),
                        self._estilo.corpo,
                    )
                )
            elementos.append(Spacer(1, 2))
        return elementos

    def _formatar_conteudo_perfil(self, conteudo: str) -> list:
        """Junta linhas consecutivas em um parágrafo; linha em branco separa parágrafos."""
        elementos = []
        prosa: list[str] = []

        def fechar_paragrafo() -> None:
            if prosa:
                elementos.append(Paragraph(self._escape_text(" ".join(prosa)), self._estilo.corpo))
                elementos.append(Spacer(1, 4))
                prosa.clear()

        for linha in conteudo.splitlines():
            linha_tratada = linha.strip()
            if not linha_tratada:
                fechar_paragrafo()
            elif linha_tratada.startswith(_MARCADORES_DE_TOPICO):
                fechar_paragrafo()
                texto = linha_tratada.lstrip("-•* ").strip()
                elementos.append(Paragraph(f"&bull;&nbsp;&nbsp;{self._escape_text(texto)}", self._estilo.corpo))
                elementos.append(Spacer(1, 2))
            else:
                prosa.append(linha_tratada)
        fechar_paragrafo()
        return elementos

    def _formatar_conteudo_tecnologias(self, conteudo: str, idioma_alvo: str = "en") -> list:
        """Uma categoria por linha, sem marcador; o rótulo vai em negrito."""
        return [
            Paragraph(
                self._aplicar_enfase(linha, TipoSecao.TECNOLOGIAS, idioma_alvo, self._catalogo),
                self._estilo.tecnologia,
            )
            for linha in self._linhas_de_tecnologias(conteudo)
        ]

    def _linhas_de_tecnologias(self, conteudo: str) -> list[str]:
        linhas: list[str] = []
        for linha in conteudo.splitlines():
            texto = linha.strip().lstrip("-•* ").strip()
            if texto:
                linhas.extend(self._quebrar_categorias(texto))
        return linhas

    def _quebrar_categorias(self, texto: str) -> list[str]:
        """Separa 'A: x, B: y' em uma linha por categoria conhecida, sem a vírgula de ligação."""
        rotulos = {
            rotulo for traducoes in self._catalogo.categorias_tecnologia.values() for rotulo in traducoes.values()
        }
        alternativas = "|".join(re.escape(rotulo) for rotulo in sorted(rotulos, key=len, reverse=True))
        antes_de_rotulo = re.compile(rf",?\s*(?=\b(?:{alternativas})\s*:)", re.IGNORECASE)
        partes = (parte.strip().rstrip(",").strip() for parte in antes_de_rotulo.split(texto))
        return [parte for parte in partes if parte]

    def _formatar_conteudo_experiencias(self, conteudo: str) -> list:
        estilo_corpo = self._estilo.corpo
        blocos = self._separar_blocos_experiencias(conteudo)
        estilo_contexto = self._estilo_contexto(estilo_corpo)
        elementos = []

        for indice_bloco, bloco in enumerate(blocos):
            for index, linha in enumerate(bloco):
                linha_tratada = linha.strip()
                if linha_tratada.startswith(("-", "•", "*")):
                    texto = linha_tratada.lstrip("-•* ").strip()
                    elementos.append(Paragraph(f"&bull;&nbsp;&nbsp;{self._escape_text(texto)}", estilo_corpo))
                    elementos.append(Spacer(1, 2))
                elif index > 0 and self._eh_linha_de_contexto(linha_tratada):
                    elementos.append(Paragraph(self._escape_text(linha_tratada), estilo_contexto))
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
    def _estilo_contexto(estilo_corpo: ParagraphStyle) -> ParagraphStyle:
        return ParagraphStyle(
            "ContextoExperiencia",
            parent=estilo_corpo,
            fontName="Helvetica-Oblique",
            textColor=HexColor("#666666"),
        )

    @staticmethod
    def _eh_linha_de_contexto(linha: str) -> bool:
        """Linha final da experiência no padrão "Contexto: ..." ou "Context: ..."."""
        rotulo, separador, _ = linha.partition(":")
        return bool(separador) and rotulo.strip().lower() in ROTULOS_CONTEXTO_RECONHECIDOS

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
