import socket

import httpx
import pytest

from jobsync.shared_kernel.adapters.cliente_http_seguro import (
    ClienteHttpSeguro,
    MotivoFalhaHttp,
    RequisicaoHttpRecusada,
)

IP_PUBLICO = "93.184.216.34"


def _resolvedor_publico(host: str) -> list[str]:
    return [IP_PUBLICO]


def _criar_cliente(handler, resolvedor=_resolvedor_publico, **opcoes) -> ClienteHttpSeguro:
    return ClienteHttpSeguro(
        transporte=httpx.MockTransport(handler),
        resolvedor=resolvedor,
        **opcoes,
    )


def _handler_ok(texto: str = "ok"):
    chamadas = []

    def handler(request: httpx.Request) -> httpx.Response:
        chamadas.append(request)
        return httpx.Response(200, text=texto, request=request)

    handler.chamadas = chamadas
    return handler


class TestClienteHttpSeguro:
    def test_obtem_pagina_e_devolve_status_texto_e_url_final(self):
        handler = _handler_ok("Vaga de Engenheiro de Software com acentuação")
        cliente = _criar_cliente(handler)

        resposta = cliente.obter("https://exemplo.com/vaga/1")

        assert resposta.status == 200
        assert resposta.texto == "Vaga de Engenheiro de Software com acentuação"
        assert resposta.url_final == "https://exemplo.com/vaga/1"

    def test_conecta_no_ip_validado_mantendo_host_e_sni_originais(self):
        handler = _handler_ok()
        cliente = _criar_cliente(handler)

        cliente.obter("https://exemplo.com/vaga/1?a=1")

        requisicao = handler.chamadas[0]
        assert requisicao.url.host == IP_PUBLICO
        assert requisicao.url.path == "/vaga/1"
        assert requisicao.url.query == b"a=1"
        assert requisicao.headers["host"] == "exemplo.com"
        assert requisicao.extensions["sni_hostname"] == "exemplo.com"

    def test_mantem_porta_no_cabecalho_host(self):
        handler = _handler_ok()
        cliente = _criar_cliente(handler)

        cliente.obter("http://exemplo.com:8080/vaga")

        assert handler.chamadas[0].headers["host"] == "exemplo.com:8080"
        assert handler.chamadas[0].url.port == 8080

    def test_envia_cabecalhos_adicionais_informados(self):
        handler = _handler_ok()
        cliente = _criar_cliente(handler)

        cliente.obter("https://exemplo.com/vaga", cabecalhos={"Accept-Language": "pt-BR"})

        assert handler.chamadas[0].headers["accept-language"] == "pt-BR"

    def test_identifica_o_cliente_no_user_agent(self):
        handler = _handler_ok()
        cliente = _criar_cliente(handler)

        cliente.obter("https://exemplo.com/vaga")

        assert "job-sync" in handler.chamadas[0].headers["user-agent"]

    def test_aceita_ip_publico_literal(self):
        handler = _handler_ok()
        cliente = _criar_cliente(handler)

        resposta = cliente.obter(f"http://{IP_PUBLICO}/vaga")

        assert resposta.status == 200

    @pytest.mark.parametrize(
        "url",
        [
            "ftp://exemplo.com/vaga",
            "file:///etc/passwd",
            "javascript:alert(1)",
            "gopher://exemplo.com/",
            "exemplo.com/vaga",
            "https://",
        ],
    )
    def test_recusa_esquemas_e_enderecos_invalidos(self, url):
        handler = _handler_ok()
        cliente = _criar_cliente(handler)

        with pytest.raises(RequisicaoHttpRecusada) as erro:
            cliente.obter(url)

        assert erro.value.motivo is MotivoFalhaHttp.ENDERECO_RECUSADO
        assert handler.chamadas == []

    @pytest.mark.parametrize(
        "url",
        [
            "http://127.0.0.1/",
            "http://127.1.2.3:8000/admin",
            "http://10.0.0.5/",
            "http://192.168.1.1/",
            "http://172.16.0.1/",
            "http://169.254.169.254/latest/meta-data/",
            "http://0.0.0.0/",
            "http://100.64.0.1/",
            "http://[::1]/",
            "http://[fd00::1]/",
            "http://[fe80::1]/",
            "http://[::ffff:127.0.0.1]/",
            "http://[::ffff:10.0.0.1]/",
            "http://[64:ff9b::7f00:1]/",
            "http://[2002:7f00:1::1]/",
        ],
    )
    def test_recusa_ips_internos_sem_fazer_a_requisicao(self, url):
        handler = _handler_ok()
        cliente = _criar_cliente(handler)

        with pytest.raises(RequisicaoHttpRecusada) as erro:
            cliente.obter(url)

        assert erro.value.motivo is MotivoFalhaHttp.ENDERECO_RECUSADO
        assert handler.chamadas == []

    def test_recusa_host_que_resolve_para_ip_privado(self):
        handler = _handler_ok()
        cliente = _criar_cliente(handler, resolvedor=lambda host: ["10.1.2.3"])

        with pytest.raises(RequisicaoHttpRecusada) as erro:
            cliente.obter("https://interno.exemplo.com/vaga")

        assert erro.value.motivo is MotivoFalhaHttp.ENDERECO_RECUSADO
        assert handler.chamadas == []

    def test_recusa_host_com_resolucao_mista_publica_e_privada(self):
        handler = _handler_ok()
        cliente = _criar_cliente(handler, resolvedor=lambda host: [IP_PUBLICO, "127.0.0.1"])

        with pytest.raises(RequisicaoHttpRecusada) as erro:
            cliente.obter("https://misto.exemplo.com/vaga")

        assert erro.value.motivo is MotivoFalhaHttp.ENDERECO_RECUSADO
        assert handler.chamadas == []

    def test_recusa_host_localhost(self):
        handler = _handler_ok()
        cliente = _criar_cliente(handler, resolvedor=lambda host: ["127.0.0.1"])

        with pytest.raises(RequisicaoHttpRecusada) as erro:
            cliente.obter("http://localhost:8000/")

        assert erro.value.motivo is MotivoFalhaHttp.ENDERECO_RECUSADO

    def test_falha_de_dns_vira_falha_de_rede(self):
        def resolvedor(host: str) -> list[str]:
            raise socket.gaierror("sem resolução")

        cliente = _criar_cliente(_handler_ok(), resolvedor=resolvedor)

        with pytest.raises(RequisicaoHttpRecusada) as erro:
            cliente.obter("https://inexistente.exemplo.com/vaga")

        assert erro.value.motivo is MotivoFalhaHttp.FALHA_DE_REDE

    def test_segue_redirecionamento_relativo_e_devolve_a_url_final(self):
        chamadas = []

        def handler(request: httpx.Request) -> httpx.Response:
            chamadas.append(request)
            if request.url.path == "/antiga":
                return httpx.Response(302, headers={"Location": "/nova"}, request=request)
            return httpx.Response(200, text="conteúdo", request=request)

        cliente = _criar_cliente(handler)

        resposta = cliente.obter("https://exemplo.com/antiga")

        assert resposta.texto == "conteúdo"
        assert resposta.url_final == "https://exemplo.com/nova"
        assert len(chamadas) == 2

    def test_recusa_redirecionamento_para_ip_interno(self):
        chamadas = []

        def handler(request: httpx.Request) -> httpx.Response:
            chamadas.append(request)
            return httpx.Response(
                302,
                headers={"Location": "http://169.254.169.254/latest/meta-data/"},
                request=request,
            )

        cliente = _criar_cliente(handler)

        with pytest.raises(RequisicaoHttpRecusada) as erro:
            cliente.obter("https://exemplo.com/vaga")

        assert erro.value.motivo is MotivoFalhaHttp.ENDERECO_RECUSADO
        assert len(chamadas) == 1

    def test_recusa_redirecionamento_para_host_que_resolve_para_ip_interno(self):
        def resolvedor(host: str) -> list[str]:
            return ["10.0.0.9"] if host == "interno.exemplo.com" else [IP_PUBLICO]

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                301, headers={"Location": "https://interno.exemplo.com/"}, request=request
            )

        cliente = _criar_cliente(handler, resolvedor=resolvedor)

        with pytest.raises(RequisicaoHttpRecusada) as erro:
            cliente.obter("https://exemplo.com/vaga")

        assert erro.value.motivo is MotivoFalhaHttp.ENDERECO_RECUSADO

    def test_recusa_redirecionamento_para_esquema_invalido(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(302, headers={"Location": "file:///etc/passwd"}, request=request)

        cliente = _criar_cliente(handler)

        with pytest.raises(RequisicaoHttpRecusada) as erro:
            cliente.obter("https://exemplo.com/vaga")

        assert erro.value.motivo is MotivoFalhaHttp.ENDERECO_RECUSADO

    def test_limita_a_quantidade_de_redirecionamentos(self):
        chamadas = []

        def handler(request: httpx.Request) -> httpx.Response:
            chamadas.append(request)
            return httpx.Response(302, headers={"Location": "/loop"}, request=request)

        cliente = _criar_cliente(handler, max_redirecionamentos=3)

        with pytest.raises(RequisicaoHttpRecusada) as erro:
            cliente.obter("https://exemplo.com/loop")

        assert erro.value.motivo is MotivoFalhaHttp.EXCESSO_REDIRECIONAMENTOS
        assert len(chamadas) == 4

    def test_recusa_corpo_acima_do_limite_de_tamanho(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, content=b"a" * 5000, request=request)

        cliente = _criar_cliente(handler, max_bytes=1000)

        with pytest.raises(RequisicaoHttpRecusada) as erro:
            cliente.obter("https://exemplo.com/vaga")

        assert erro.value.motivo is MotivoFalhaHttp.TAMANHO_EXCEDIDO

    def test_recusa_content_length_acima_do_limite_de_tamanho(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200, headers={"Content-Length": "999999"}, content=b"a", request=request
            )

        cliente = _criar_cliente(handler, max_bytes=1000)

        with pytest.raises(RequisicaoHttpRecusada) as erro:
            cliente.obter("https://exemplo.com/vaga")

        assert erro.value.motivo is MotivoFalhaHttp.TAMANHO_EXCEDIDO

    def test_aceita_corpo_no_limite_de_tamanho(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, content=b"a" * 1000, request=request)

        cliente = _criar_cliente(handler, max_bytes=1000)

        resposta = cliente.obter("https://exemplo.com/vaga")

        assert len(resposta.texto) == 1000

    def test_tempo_esgotado_na_rede_vira_motivo_proprio(self):
        def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ReadTimeout("lento", request=request)

        cliente = _criar_cliente(handler)

        with pytest.raises(RequisicaoHttpRecusada) as erro:
            cliente.obter("https://exemplo.com/vaga")

        assert erro.value.motivo is MotivoFalhaHttp.TEMPO_ESGOTADO

    def test_tempo_total_considera_todos_os_redirecionamentos(self):
        relogio = iter([0.0, 0.0, 20.0, 20.0, 20.0, 20.0])

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(302, headers={"Location": "/proxima"}, request=request)

        cliente = _criar_cliente(handler, timeout_segundos=15.0, relogio=lambda: next(relogio))

        with pytest.raises(RequisicaoHttpRecusada) as erro:
            cliente.obter("https://exemplo.com/inicio")

        assert erro.value.motivo is MotivoFalhaHttp.TEMPO_ESGOTADO

    def test_falha_de_conexao_vira_falha_de_rede(self):
        def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError("recusada", request=request)

        cliente = _criar_cliente(handler)

        with pytest.raises(RequisicaoHttpRecusada) as erro:
            cliente.obter("https://exemplo.com/vaga")

        assert erro.value.motivo is MotivoFalhaHttp.FALHA_DE_REDE

    def test_nao_repete_a_requisicao_quando_o_site_responde_429(self):
        chamadas = []

        def handler(request: httpx.Request) -> httpx.Response:
            chamadas.append(request)
            return httpx.Response(429, text="muitas requisições", request=request)

        cliente = _criar_cliente(handler)

        resposta = cliente.obter("https://exemplo.com/vaga")

        assert resposta.status == 429
        assert len(chamadas) == 1

    def test_devolve_status_de_erro_sem_levantar_excecao(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(404, text="não encontrada", request=request)

        cliente = _criar_cliente(handler)

        resposta = cliente.obter("https://exemplo.com/vaga")

        assert resposta.status == 404

    def test_decodifica_corpo_com_charset_informado_no_cabecalho(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                headers={"Content-Type": "text/html; charset=iso-8859-1"},
                content="Programação".encode("iso-8859-1"),
                request=request,
            )

        cliente = _criar_cliente(handler)

        resposta = cliente.obter("https://exemplo.com/vaga")

        assert resposta.texto == "Programação"
