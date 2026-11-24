from pathlib import Path

import pytest

from jobsync.shared_kernel.adapters.cliente_http_seguro import (
    MotivoFalhaHttp,
    RequisicaoHttpRecusada,
    RespostaHttp,
)
from jobsync.vaga import LeituraVagaIndisponivel, LinkVaga, MotivoLeituraIndisponivel
from jobsync.vaga.adapters import LeitorVagaLinkedInClient

URL_VAGA = "https://www.linkedin.com/jobs/view/1234567890/"
URL_VISITANTE = "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/1234567890"
HTML_VAGA = (Path(__file__).parent / "fixtures" / "linkedin_vaga_visitante.html").read_text(encoding="utf-8")


class ClienteHttpFake:
    def __init__(self, resposta=None, erro=None):
        self.resposta = resposta
        self.erro = erro
        self.urls: list[str] = []
        self.cabecalhos: list = []

    def obter(self, url, cabecalhos=None):
        self.urls.append(url)
        self.cabecalhos.append(cabecalhos)
        if self.erro:
            raise self.erro
        return self.resposta


def _leitor(html: str = HTML_VAGA, status: int = 200, erro=None):
    cliente = ClienteHttpFake(resposta=RespostaHttp(status=status, texto=html, url_final=URL_VISITANTE), erro=erro)
    return LeitorVagaLinkedInClient(cliente_http=cliente), cliente


class TestLeitorVagaLinkedInClient:
    def test_busca_a_versao_publica_da_vaga_a_partir_do_id(self):
        leitor, cliente = _leitor()

        leitor.ler(LinkVaga.criar(URL_VAGA))

        assert cliente.urls == [URL_VISITANTE]

    def test_nao_envia_credenciais_nem_cookies(self):
        leitor, cliente = _leitor()

        leitor.ler(LinkVaga.criar(URL_VAGA))

        nomes = {nome.lower() for nome in cliente.cabecalhos[0]}
        assert nomes <= {"accept", "accept-language"}

    def test_le_cargo_empresa_e_local(self):
        leitor, _ = _leitor()

        dados = leitor.ler(LinkVaga.criar(URL_VAGA))

        assert dados.cargo == "Engenheiro de Software Sênior"
        assert dados.empresa == "Empresa Exemplo"
        assert dados.local == "Brazil"
        assert dados.url == URL_VAGA

    def test_le_os_criterios_da_vaga(self):
        leitor, _ = _leitor()

        dados = leitor.ler(LinkVaga.criar(URL_VAGA))

        assert dados.senioridade == "Mid-Senior level"
        assert dados.tipo_contratacao == "Tempo integral"
        assert dados.setor == "Financial Services"

    def test_preserva_a_descricao_original_com_titulos_e_listas(self):
        leitor, _ = _leitor()

        dados = leitor.ler(LinkVaga.criar(URL_VAGA))

        assert dados.descricao == (
            "Sobre a Empresa Exemplo\n\n"
            "Construímos a plataforma financeira para empresas no Brasil.\n\n"
            "O que você vai fazer\n\n"
            "- Construir e evoluir APIs em Python\n"
            "- Preparar soluções para produção, com testes e observabilidade\n\n"
            "O que buscamos\n\n"
            "- Experiência sólida com Python e FastAPI\n"
            "- Conhecimento de bancos de dados e integrações\n\n"
            "Modelo de trabalho: remoto, com presença no escritório apenas para eventos táticos."
        )

    def test_nao_inclui_dados_de_contexto_nem_elementos_da_pagina(self):
        leitor, _ = _leitor()

        dados = leitor.ler(LinkVaga.criar(URL_VAGA))

        textos = " ".join(filter(None, [dados.descricao, dados.cargo, dados.empresa, dados.local]))
        for indesejado in ("applicants", "weeks ago", "Show more", "sign in", "Referrals", "Apply"):
            assert indesejado not in textos

    def test_le_criterios_com_rotulos_em_portugues(self):
        html = (
            HTML_VAGA.replace("Seniority level", "Nível de experiência")
            .replace("Employment type", "Tipo de emprego")
            .replace("Industries", "Setores")
            .replace("Mid-Senior level", "Pleno-sênior")
            .replace("Full-time", "Tempo integral")
            .replace("Financial Services", "Serviços financeiros")
        )
        leitor, _ = _leitor(html)

        dados = leitor.ler(LinkVaga.criar(URL_VAGA))

        assert dados.senioridade == "Pleno-sênior"
        assert dados.tipo_contratacao == "Tempo integral"
        assert dados.setor == "Serviços financeiros"

    @pytest.mark.parametrize("valor", ["Not Applicable", "Não aplicável"])
    def test_ignora_senioridade_nao_aplicavel(self, valor):
        leitor, _ = _leitor(HTML_VAGA.replace("Mid-Senior level", valor))

        dados = leitor.ler(LinkVaga.criar(URL_VAGA))

        assert dados.senioridade is None

    def test_devolve_a_vaga_mesmo_sem_criterios_e_sem_local(self):
        html = (
            HTML_VAGA.replace('class="description__job-criteria-list"', 'class="outra-lista" hidden')
            .replace("description__job-criteria-item", "outro-item")
            .replace('<span class="topcard__flavor topcard__flavor--bullet">\n              Brazil\n            </span>', "")
        )
        leitor, _ = _leitor(html)

        dados = leitor.ler(LinkVaga.criar(URL_VAGA))

        assert dados.cargo == "Engenheiro de Software Sênior"
        assert dados.local is None
        assert dados.senioridade is None
        assert dados.tipo_contratacao is None
        assert dados.setor is None

    @pytest.mark.parametrize(
        "html",
        [
            "",
            "<html><body><h1>Entre para continuar</h1><form><input name='session_key'></form></body></html>",
            HTML_VAGA.replace("top-card-layout__title", "outra-classe"),
            HTML_VAGA.replace("show-more-less-html__markup", "outra-classe"),
        ],
    )
    def test_pagina_sem_titulo_ou_descricao_nao_traz_dados(self, html):
        leitor, _ = _leitor(html)

        with pytest.raises(LeituraVagaIndisponivel) as erro:
            leitor.ler(LinkVaga.criar(URL_VAGA))

        assert erro.value.motivo is MotivoLeituraIndisponivel.SEM_DADOS

    def test_bloqueio_nao_gera_nova_tentativa(self):
        leitor, cliente = _leitor(html="desafio anti-bot", status=429)

        with pytest.raises(LeituraVagaIndisponivel) as erro:
            leitor.ler(LinkVaga.criar(URL_VAGA))

        assert erro.value.motivo is MotivoLeituraIndisponivel.BLOQUEADA
        assert len(cliente.urls) == 1

    def test_vaga_inexistente_e_nao_encontrada(self):
        leitor, _ = _leitor(html="", status=404)

        with pytest.raises(LeituraVagaIndisponivel) as erro:
            leitor.ler(LinkVaga.criar(URL_VAGA))

        assert erro.value.motivo is MotivoLeituraIndisponivel.NAO_ENCONTRADA

    def test_traduz_falha_do_cliente_http_em_motivo(self):
        leitor, _ = _leitor(erro=RequisicaoHttpRecusada(MotivoFalhaHttp.TEMPO_ESGOTADO))

        with pytest.raises(LeituraVagaIndisponivel) as erro:
            leitor.ler(LinkVaga.criar(URL_VAGA))

        assert erro.value.motivo is MotivoLeituraIndisponivel.TEMPO_ESGOTADO

    def test_recusa_link_que_nao_e_do_linkedin(self):
        leitor, cliente = _leitor()

        with pytest.raises(ValueError):
            leitor.ler(LinkVaga.criar("https://empresa.gupy.io/jobs/123456"))

        assert cliente.urls == []
