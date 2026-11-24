import json

import pytest

from jobsync.shared_kernel.adapters.cliente_http_seguro import (
    MotivoFalhaHttp,
    RequisicaoHttpRecusada,
    RespostaHttp,
)
from jobsync.vaga import (
    DadosVaga,
    LeituraVagaIndisponivel,
    LinkVaga,
    MotivoLeituraIndisponivel,
)
from jobsync.vaga.adapters import LeitorVagaGenericoClient

URL = "https://empresa.gupy.io/jobs/123456"
TEXTO_LONGO = "Conteúdo de uma página de vaga com texto suficiente para ser considerado. " * 3


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


class ExtratorTextoFake:
    def __init__(self, dados=None):
        self.dados = dados
        self.textos: list[str] = []

    def extrair(self, texto: str) -> DadosVaga:
        self.textos.append(texto)
        return self.dados or DadosVaga(descricao=texto, cargo="Cargo da IA", empresa="Empresa da IA")


def _html_com_json_ld(dados) -> str:
    return (
        "<html><head><script type='application/ld+json'>"
        + json.dumps(dados)
        + "</script></head><body><p>corpo</p></body></html>"
    )


def _job_posting(**extras) -> dict:
    dados = {
        "@context": "https://schema.org",
        "@type": "JobPosting",
        "title": "Engenheiro de Software",
        "description": "<p>Descrição da vaga.</p><ul><li>Python</li><li>SQL</li></ul>",
        "hiringOrganization": {"@type": "Organization", "name": "Empresa X"},
        "jobLocation": {
            "@type": "Place",
            "address": {"addressLocality": "São Paulo", "addressRegion": "SP", "addressCountry": "BR"},
        },
        "employmentType": "FULL_TIME",
        "industry": "Tecnologia",
    }
    dados.update(extras)
    return dados


def _leitor(resposta=None, erro=None, extrator=None):
    cliente = ClienteHttpFake(resposta=resposta, erro=erro)
    extrator = extrator or ExtratorTextoFake()
    return LeitorVagaGenericoClient(cliente_http=cliente, extrator_texto=extrator), cliente, extrator


def _resposta(html: str, status: int = 200) -> RespostaHttp:
    return RespostaHttp(status=status, texto=html, url_final=URL)


class TestLeitorVagaGenericoClient:
    def test_le_os_dados_do_json_ld_sem_chamar_a_ia(self):
        leitor, cliente, extrator = _leitor(_resposta(_html_com_json_ld(_job_posting())))

        dados = leitor.ler(LinkVaga.criar(URL))

        assert dados.cargo == "Engenheiro de Software"
        assert dados.empresa == "Empresa X"
        assert dados.local == "São Paulo, SP, BR"
        assert dados.tipo_contratacao == "Tempo integral"
        assert dados.setor == "Tecnologia"
        assert dados.descricao == "Descrição da vaga.\n\n- Python\n- SQL"
        assert dados.url == URL
        assert extrator.textos == []
        assert cliente.urls == [URL]

    def test_envia_cabecalhos_de_idioma_e_tipo_de_conteudo(self):
        leitor, cliente, _ = _leitor(_resposta(_html_com_json_ld(_job_posting())))

        leitor.ler(LinkVaga.criar(URL))

        assert "pt-BR" in cliente.cabecalhos[0]["Accept-Language"]
        assert "text/html" in cliente.cabecalhos[0]["Accept"]

    def test_encontra_o_job_posting_dentro_de_graph(self):
        html = _html_com_json_ld({"@context": "https://schema.org", "@graph": [{"@type": "WebSite"}, _job_posting()]})
        leitor, _, _ = _leitor(_resposta(html))

        dados = leitor.ler(LinkVaga.criar(URL))

        assert dados.cargo == "Engenheiro de Software"

    def test_encontra_o_job_posting_em_lista_de_objetos(self):
        html = _html_com_json_ld([{"@type": "BreadcrumbList"}, _job_posting()])
        leitor, _, _ = _leitor(_resposta(html))

        dados = leitor.ler(LinkVaga.criar(URL))

        assert dados.empresa == "Empresa X"

    def test_aceita_tipo_como_lista_e_empresa_como_texto(self):
        posting = _job_posting(**{"@type": ["JobPosting", "Thing"], "hiringOrganization": "Empresa Y"})
        leitor, _, _ = _leitor(_resposta(_html_com_json_ld(posting)))

        dados = leitor.ler(LinkVaga.criar(URL))

        assert dados.empresa == "Empresa Y"

    def test_decodifica_descricao_com_html_escapado(self):
        posting = _job_posting(description="&lt;p&gt;Texto escapado&lt;/p&gt;&lt;ul&gt;&lt;li&gt;Item&lt;/li&gt;&lt;/ul&gt;")
        leitor, _, _ = _leitor(_resposta(_html_com_json_ld(posting)))

        dados = leitor.ler(LinkVaga.criar(URL))

        assert dados.descricao == "Texto escapado\n\n- Item"

    def test_usa_remoto_como_local_quando_a_vaga_e_teletrabalho(self):
        posting = _job_posting(jobLocationType="TELECOMMUTE")
        del posting["jobLocation"]
        leitor, _, _ = _leitor(_resposta(_html_com_json_ld(posting)))

        dados = leitor.ler(LinkVaga.criar(URL))

        assert dados.local == "Remoto"

    def test_junta_locais_quando_ha_varios(self):
        posting = _job_posting(
            jobLocation=[
                {"address": {"addressLocality": "Recife", "addressCountry": {"name": "Brasil"}}},
                {"address": {"addressLocality": "Lisboa"}},
            ]
        )
        leitor, _, _ = _leitor(_resposta(_html_com_json_ld(posting)))

        dados = leitor.ler(LinkVaga.criar(URL))

        assert dados.local == "Recife, Brasil; Lisboa"

    def test_mantem_valor_original_para_tipo_de_contratacao_desconhecido(self):
        posting = _job_posting(employmentType=["CONTRACTOR", "OUTRO_TIPO"])
        leitor, _, _ = _leitor(_resposta(_html_com_json_ld(posting)))

        dados = leitor.ler(LinkVaga.criar(URL))

        assert dados.tipo_contratacao == "Contrato, OUTRO_TIPO"

    def test_usa_a_ia_com_o_texto_da_pagina_quando_nao_ha_json_ld(self):
        html = (
            "<html><head><style>.x{}</style></head><body><nav>Menu do site</nav>"
            f"<main><h1>Engenheiro</h1><p>{TEXTO_LONGO}</p></main><footer>Rodapé</footer></body></html>"
        )
        leitor, _, extrator = _leitor(_resposta(html))

        dados = leitor.ler(LinkVaga.criar(URL))

        assert dados.cargo == "Cargo da IA"
        assert dados.url == URL
        assert "Engenheiro" in extrator.textos[0]
        assert "Menu do site" not in extrator.textos[0]
        assert "Rodapé" not in extrator.textos[0]

    def test_usa_a_ia_quando_o_json_ld_e_invalido(self):
        html = (
            "<html><head><script type='application/ld+json'>{ não é json </script></head>"
            f"<body><p>{TEXTO_LONGO}</p></body></html>"
        )
        leitor, _, extrator = _leitor(_resposta(html))

        dados = leitor.ler(LinkVaga.criar(URL))

        assert dados.cargo == "Cargo da IA"
        assert len(extrator.textos) == 1

    def test_usa_a_ia_quando_o_json_ld_nao_e_de_vaga(self):
        html = _html_com_json_ld({"@type": "Organization", "name": "Empresa"}).replace(
            "<p>corpo</p>", f"<p>{TEXTO_LONGO}</p>"
        )
        leitor, _, extrator = _leitor(_resposta(html))

        leitor.ler(LinkVaga.criar(URL))

        assert len(extrator.textos) == 1

    def test_usa_a_ia_quando_o_json_ld_nao_tem_descricao(self):
        posting = _job_posting(description="")
        html = _html_com_json_ld(posting).replace("<p>corpo</p>", f"<p>{TEXTO_LONGO}</p>")
        leitor, _, extrator = _leitor(_resposta(html))

        leitor.ler(LinkVaga.criar(URL))

        assert len(extrator.textos) == 1

    def test_pagina_com_pouco_texto_nao_traz_dados(self):
        leitor, _, extrator = _leitor(_resposta("<html><body><p>Ative o JavaScript</p></body></html>"))

        with pytest.raises(LeituraVagaIndisponivel) as erro:
            leitor.ler(LinkVaga.criar(URL))

        assert erro.value.motivo is MotivoLeituraIndisponivel.SEM_DADOS
        assert extrator.textos == []

    @pytest.mark.parametrize(
        "status, motivo",
        [
            (403, MotivoLeituraIndisponivel.BLOQUEADA),
            (429, MotivoLeituraIndisponivel.BLOQUEADA),
            (404, MotivoLeituraIndisponivel.NAO_ENCONTRADA),
            (503, MotivoLeituraIndisponivel.FALHA_DE_REDE),
        ],
    )
    def test_traduz_status_http_de_erro_em_motivo(self, status, motivo):
        leitor, _, extrator = _leitor(_resposta("erro", status=status))

        with pytest.raises(LeituraVagaIndisponivel) as erro:
            leitor.ler(LinkVaga.criar(URL))

        assert erro.value.motivo is motivo
        assert extrator.textos == []

    @pytest.mark.parametrize(
        "falha, motivo",
        [
            (MotivoFalhaHttp.ENDERECO_RECUSADO, MotivoLeituraIndisponivel.ENDERECO_RECUSADO),
            (MotivoFalhaHttp.TEMPO_ESGOTADO, MotivoLeituraIndisponivel.TEMPO_ESGOTADO),
            (MotivoFalhaHttp.FALHA_DE_REDE, MotivoLeituraIndisponivel.FALHA_DE_REDE),
        ],
    )
    def test_traduz_falha_do_cliente_http_em_motivo(self, falha, motivo):
        leitor, _, _ = _leitor(erro=RequisicaoHttpRecusada(falha))

        with pytest.raises(LeituraVagaIndisponivel) as erro:
            leitor.ler(LinkVaga.criar(URL))

        assert erro.value.motivo is motivo

    def test_limita_o_texto_da_pagina_ao_tamanho_maximo_da_descricao(self):
        html = f"<html><body><p>{'palavra ' * 20_000}</p></body></html>"
        leitor, _, extrator = _leitor(_resposta(html))

        leitor.ler(LinkVaga.criar(URL))

        assert len(extrator.textos[0]) <= 50_000
