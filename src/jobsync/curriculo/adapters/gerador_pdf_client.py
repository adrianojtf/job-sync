"""Adapter (implementa GeradorPdfPort) que gera o PDF final do currículo com ReportLab.

O layout segue o modelo de referência do JOB-0016: cabeçalho centralizado com o nome em
caixa alta e o contato com link, seções com título em caixa alta e linha azul-marinho,
tecnologias uma categoria por linha e corpo em parágrafos conforme o conteúdo de cada seção.
Cores, tamanhos e fontes vêm de `EstiloCurriculoPdf`.
"""
from __future__ import annotations

import io
import logging
import re

from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from jobsync.curriculo import Curriculo, TipoSecao
from jobsync.curriculo.adapters.pdf.estilo_curriculo_pdf import EstiloCurriculoPdf
from jobsync.curriculo.adapters.pdf.interpretador_experiencias import (
    BlocoExperiencia,
    InterpretadorExperiencias,
)
from jobsync.curriculo.adapters.pdf.registrador_fontes_pdf import RegistradorFontesPdf
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
logger = logging.getLogger(__name__)

_MARGEM_SUPERIOR = 29.5  # com a folga do frame, o topo do nome fica em 39,5 pt, como no modelo
_MARGEM_INFERIOR = 36
_MARCADOR_DA_LISTA = "●"
_LINHA_DE_IDIOMA = re.compile(r"^(?P<idioma>.+?)(?:(?P<travessao>\s+[—–-]\s+)|\s*:\s*)(?P<nivel>.+)$")
_SEPARADOR_DO_CONTATO = "&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;"  # mais largo que um espaço, como no modelo
_FOLGA_LATERAL_DO_FRAME = 6  # padding interno do Frame do ReportLab, somado à margem do documento
_MARCADORES_DE_TOPICO = ("-", "•", "*")
_ROTULO_DE_CATEGORIA = re.compile(r"^(?P<prefixo>[-•*]\s*)?(?P<label>[^:\n]+?)\s*:", re.MULTILINE)


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
        self._interpretador = InterpretadorExperiencias()

    def gerar(self, curriculo: Curriculo, idioma_alvo: str) -> bytes:
        buffer = io.BytesIO()
        documento = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=self._estilo.margem_lateral - _FOLGA_LATERAL_DO_FRAME,
            rightMargin=self._estilo.margem_lateral - _FOLGA_LATERAL_DO_FRAME,
            topMargin=_MARGEM_SUPERIOR,
            bottomMargin=_MARGEM_INFERIOR,
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
            elementos.append(Paragraph(_SEPARADOR_DO_CONTATO.join(partes_do_contato), self._estilo.contato))
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
            elementos.append(Paragraph(self._escape_text(titulo_localizado.upper()), self._estilo.titulo_secao))
            elementos.append(self._linha_da_secao())
            elementos.extend(self._formatar_conteudo(secao.conteudo, tipo, idioma_alvo))
        return elementos

    def _linha_da_secao(self) -> HRFlowable:
        linha = HRFlowable(
            width="100%",
            thickness=self._estilo.espessura_linha_secao,
            color=self._estilo.cor_destaque,
            spaceBefore=2,
            spaceAfter=6.5,
        )
        linha.keepWithNext = 1  # o título, a linha e o começo do conteúdo não se separam entre páginas
        return linha

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
        """Destaca o texto antes do primeiro ":" de cada linha, seja ele do catálogo ou criado pelo usuário."""
        texto_localizado = GeradorPdfClient._traduzir_categorias_tecnologia(conteudo, idioma_alvo, catalogo)
        return _ROTULO_DE_CATEGORIA.sub(
            lambda m: f"{m.group('prefixo') or ''}<b>{m.group('label').strip()}:</b>", texto_localizado
        )

    def _formatar_conteudo(
        self,
        conteudo: str,
        tipo_secao: TipoSecao,
        idioma_alvo: str = "en",
    ) -> list:
        """Despacha para o formatador da seção; experiências, formação e certificações usam blocos."""
        if tipo_secao == TipoSecao.TECNOLOGIAS:
            return self._formatar_conteudo_tecnologias(conteudo, idioma_alvo)
        if tipo_secao == TipoSecao.PERFIL:
            return self._formatar_conteudo_perfil(conteudo)
        if tipo_secao == TipoSecao.IDIOMAS:
            return self._formatar_conteudo_idiomas(conteudo)
        return self._formatar_conteudo_em_blocos(conteudo)

    def _formatar_conteudo_perfil(self, conteudo: str) -> list:
        """Junta linhas consecutivas em um parágrafo; linha em branco separa parágrafos."""
        elementos = []
        prosa: list[str] = []

        def fechar_paragrafo() -> None:
            if prosa:
                elementos.append(Paragraph(self._escape_text(" ".join(prosa)), self._estilo.perfil))
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

    def _formatar_conteudo_idiomas(self, conteudo: str) -> list:
        """Uma linha por idioma: o idioma em negrito e o nível em texto regular."""
        linhas = (linha.strip().lstrip("-•* ").strip() for linha in conteudo.splitlines())
        return [Paragraph(self._linha_de_idioma(linha), self._estilo.idioma) for linha in linhas if linha]

    def _linha_de_idioma(self, linha: str) -> str:
        correspondencia = _LINHA_DE_IDIOMA.match(linha)
        if not correspondencia:
            return f"<b>{self._escape_text(linha)}</b>"
        idioma = self._escape_text(correspondencia.group("idioma"))
        nivel = self._escape_text(correspondencia.group("nivel"))
        if correspondencia.group("travessao"):
            separador = correspondencia.group("travessao").strip()
            return f"<b>{idioma}</b> {separador} {nivel}"
        return f"<b>{idioma}:</b> {nivel}"

    def _formatar_conteudo_em_blocos(self, conteudo: str) -> list:
        blocos = self._interpretador.interpretar(conteudo)
        logger.debug(
            "Blocos interpretados: blocos=%d topicos=%d sem_periodo=%d",
            len(blocos),
            sum(len(bloco.topicos) for bloco in blocos),
            sum(1 for bloco in blocos if not bloco.periodo),
        )
        elementos = []
        for bloco in blocos:
            elementos.extend(self._montar_bloco_de_experiencia(bloco))
        return elementos

    def _montar_bloco_de_experiencia(self, bloco: BlocoExperiencia) -> list:
        """Empresa e período, cargo e o conteúdo da experiência (também para formação).

        Com cabeçalhos de bloco: contexto, responsabilidades, realizações e skills. Sem eles,
        o layout anterior: tópicos, texto solto e contexto.
        """
        itens = []
        if bloco.cargo:
            itens.append(Paragraph(self._escape_text(bloco.cargo), self._estilo.cargo))
        if bloco.estruturado:
            itens.extend(self._itens_por_blocos(bloco))
        else:
            itens.extend(self._topicos(bloco.topicos))
            itens.extend(Paragraph(self._escape_text(linha), self._estilo.corpo) for linha in bloco.descricao)
            if bloco.contexto:
                itens.append(Paragraph(self._escape_text(bloco.contexto), self._estilo.contexto))

        return [self._linha_de_empresa_e_periodo(bloco), *itens]

    def _itens_por_blocos(self, bloco: BlocoExperiencia) -> list:
        itens = []
        if bloco.contexto:
            itens.append(Paragraph(self._escape_text(bloco.contexto), self._estilo.contexto))
        itens.extend(Paragraph(self._escape_text(linha), self._estilo.corpo) for linha in bloco.descricao)
        itens.extend(self._lista_com_rotulo(bloco.rotulo_responsabilidades, bloco.responsabilidades))
        itens.extend(self._lista_com_rotulo(bloco.rotulo_realizacoes, bloco.realizacoes))
        itens.extend(self._topicos(bloco.topicos))
        if bloco.skills:
            linha = f"{bloco.rotulo_skills}: {' | '.join(bloco.skills)}"
            itens.append(Paragraph(self._escape_text(linha), self._estilo.skills))
        return itens

    def _lista_com_rotulo(self, rotulo: str, itens: tuple[str, ...]) -> list:
        if not itens:
            return []
        return [Paragraph(self._escape_text(f"{rotulo}:"), self._estilo.rotulo_de_bloco), *self._topicos(itens)]

    def _topicos(self, topicos: tuple[str, ...]) -> list:
        return [
            Paragraph(self._escape_text(topico), self._estilo.topico, bulletText=_MARCADOR_DA_LISTA)
            for topico in topicos
        ]

    def _linha_de_empresa_e_periodo(self, bloco: BlocoExperiencia):
        empresa = Paragraph(self._escape_text(bloco.empresa), self._estilo.empresa)
        if not bloco.periodo:
            return empresa

        periodo = Paragraph(self._escape_text(bloco.periodo), self._estilo.periodo)
        largura_util = letter[0] - 2 * self._estilo.margem_lateral
        largura_da_linha = largura_util - self._estilo.recuo_direito_periodo
        tabela = Table(
            [[empresa, periodo]],
            colWidths=[largura_da_linha - self._estilo.largura_periodo, self._estilo.largura_periodo],
            hAlign="LEFT",
            spaceBefore=self._estilo.espaco_antes_da_empresa,
        )
        tabela.setStyle(
            TableStyle(
                [
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (1, 0), (1, 0), 1),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        tabela.keepWithNext = 1
        return tabela
