"""Leitor de vagas para sites em geral (Gupy, Greenhouse, Lever, páginas de carreira).

Busca a página pelo cliente HTTP seguro e lê o JSON-LD `JobPosting`. Sem ele,
usa o texto da página e o extrator de dados por IA.
"""
from __future__ import annotations

import dataclasses
import logging

from jobsync.shared_kernel.adapters.cliente_http_seguro import ClienteHttpSeguro, RequisicaoHttpRecusada
from jobsync.vaga.adapters.html_para_texto import converter_html_em_texto
from jobsync.vaga.adapters.json_ld_job_posting import extrair_dados_job_posting
from jobsync.vaga.adapters.motivos_leitura import motivo_por_falha_http, motivo_por_status_http
from jobsync.vaga.domain.dados_vaga import DadosVaga
from jobsync.vaga.domain.exceptions import LeituraVagaIndisponivel, MotivoLeituraIndisponivel
from jobsync.vaga.domain.extrator_dados_vaga_de_texto_port import ExtratorDadosVagaDeTextoPort
from jobsync.vaga.domain.leitor_vaga_por_link_port import LeitorVagaPorLinkPort
from jobsync.vaga.domain.link_vaga import LinkVaga

logger = logging.getLogger(__name__)

_TAMANHO_MINIMO_TEXTO = 100
_TAMANHO_MAXIMO_TEXTO = 50_000
_TAGS_IGNORADAS = ("nav", "footer", "aside", "form", "noscript", "svg", "iframe")
_CABECALHOS = {
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}


class LeitorVagaGenericoClient(LeitorVagaPorLinkPort):
    """Lê vagas de sites que publicam a página em HTML aberto."""

    def __init__(self, cliente_http: ClienteHttpSeguro, extrator_texto: ExtratorDadosVagaDeTextoPort) -> None:
        self._cliente_http = cliente_http
        self._extrator_texto = extrator_texto

    def ler(self, link: LinkVaga) -> DadosVaga:
        pagina = self._buscar_pagina(link)

        dados = extrair_dados_job_posting(pagina, link.url)
        if dados is not None:
            return dados

        texto = converter_html_em_texto(pagina, ignorar_tags=_TAGS_IGNORADAS)
        if len(texto) < _TAMANHO_MINIMO_TEXTO:
            raise LeituraVagaIndisponivel(MotivoLeituraIndisponivel.SEM_DADOS)
        dados = self._extrator_texto.extrair(texto[:_TAMANHO_MAXIMO_TEXTO])
        return dataclasses.replace(dados, url=dados.url or link.url)

    def _buscar_pagina(self, link: LinkVaga) -> str:
        try:
            resposta = self._cliente_http.obter(link.url, cabecalhos=_CABECALHOS)
        except RequisicaoHttpRecusada as erro:
            raise LeituraVagaIndisponivel(motivo_por_falha_http(erro.motivo)) from erro
        if not 200 <= resposta.status < 300:
            raise LeituraVagaIndisponivel(motivo_por_status_http(resposta.status))
        return resposta.texto
