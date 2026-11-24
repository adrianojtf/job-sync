"""Leitor de vagas do LinkedIn pela versão pública da vaga, visível a visitantes sem login.

Faz uma única requisição por link. Não usa credenciais, não repete a requisição
após bloqueio e não tenta contornar proteções do site: em caso de bloqueio, a
leitura falha e a pessoa é orientada a colar o texto da vaga. O endereço usado
não é documentado pelo LinkedIn e pode mudar ou deixar de responder.
"""
from __future__ import annotations

from jobsync.shared_kernel.adapters.cliente_http_seguro import ClienteHttpSeguro, RequisicaoHttpRecusada
from jobsync.vaga.adapters.interpretador_html_vaga_linkedin import interpretar_html_vaga_linkedin
from jobsync.vaga.adapters.motivos_leitura import motivo_por_falha_http, motivo_por_status_http
from jobsync.vaga.domain.dados_vaga import DadosVaga
from jobsync.vaga.domain.exceptions import LeituraVagaIndisponivel, MotivoLeituraIndisponivel
from jobsync.vaga.domain.leitor_vaga_por_link_port import LeitorVagaPorLinkPort
from jobsync.vaga.domain.link_vaga import FonteVaga, LinkVaga

_URL_VISITANTE = "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{id_vaga}"
_CABECALHOS = {
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}


class LeitorVagaLinkedInClient(LeitorVagaPorLinkPort):
    """Lê uma vaga do LinkedIn a partir do identificador presente no link."""

    def __init__(self, cliente_http: ClienteHttpSeguro) -> None:
        self._cliente_http = cliente_http

    def ler(self, link: LinkVaga) -> DadosVaga:
        if link.fonte is not FonteVaga.LINKEDIN or link.id_vaga is None:
            raise ValueError("O leitor do LinkedIn só aceita links de vaga do LinkedIn.")

        pagina = self._buscar(_URL_VISITANTE.format(id_vaga=link.id_vaga))
        dados = interpretar_html_vaga_linkedin(pagina, link.url)
        if dados is None:
            raise LeituraVagaIndisponivel(MotivoLeituraIndisponivel.SEM_DADOS)
        return dados

    def _buscar(self, url: str) -> str:
        try:
            resposta = self._cliente_http.obter(url, cabecalhos=_CABECALHOS)
        except RequisicaoHttpRecusada as erro:
            raise LeituraVagaIndisponivel(motivo_por_falha_http(erro.motivo)) from erro
        if not 200 <= resposta.status < 300:
            raise LeituraVagaIndisponivel(motivo_por_status_http(resposta.status))
        return resposta.texto
