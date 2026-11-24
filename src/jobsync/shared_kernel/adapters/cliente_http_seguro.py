"""Cliente HTTP com proteção contra SSRF para ler páginas informadas por usuários.

Para cada requisição, e para cada redirecionamento, o cliente resolve o DNS,
recusa endereços que não sejam públicos e conecta no IP já validado, mantendo
o nome original no cabeçalho `Host` e no SNI. Também limita redirecionamentos,
tamanho da resposta e tempo total. Respostas HTTP de erro (como 404 e 429) são
devolvidas ao chamador, e nunca repetidas.
"""
from __future__ import annotations

import ipaddress
import socket
import time
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Mapping, Optional, Sequence
from urllib.parse import urljoin, urlsplit, urlunsplit

import httpx

_ESQUEMAS_ACEITOS = ("http", "https")
_CODIGOS_DE_REDIRECIONAMENTO = frozenset({301, 302, 303, 307, 308})
_USER_AGENT = "Mozilla/5.0 (compatible; job-sync/1.0)"
_REDES_BLOQUEADAS = tuple(
    ipaddress.ip_network(rede)
    for rede in ("100.64.0.0/10", "64:ff9b::/96", "64:ff9b:1::/48", "2002::/16")
)


class MotivoFalhaHttp(Enum):
    """Motivos pelos quais o cliente não devolveu uma resposta."""

    ENDERECO_RECUSADO = "endereco_recusado"
    EXCESSO_REDIRECIONAMENTOS = "excesso_redirecionamentos"
    TAMANHO_EXCEDIDO = "tamanho_excedido"
    TEMPO_ESGOTADO = "tempo_esgotado"
    FALHA_DE_REDE = "falha_de_rede"


class RequisicaoHttpRecusada(Exception):
    """A requisição foi recusada ou falhou; `motivo` diz por quê."""

    def __init__(self, motivo: MotivoFalhaHttp, detalhe: str = "") -> None:
        super().__init__(f"{motivo.value}: {detalhe}" if detalhe else motivo.value)
        self.motivo = motivo


@dataclass(frozen=True)
class RespostaHttp:
    """Resposta final de uma requisição, já com os redirecionamentos seguidos."""

    status: int
    texto: str
    url_final: str


@dataclass(frozen=True)
class _Redirecionamento:
    destino: str


def _resolver_dns(host: str) -> Sequence[str]:
    informacoes = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    return list(dict.fromkeys(info[4][0] for info in informacoes))


def _ip_publico(ip: str) -> bool:
    try:
        endereco = ipaddress.ip_address(ip)
    except ValueError:
        return False
    if isinstance(endereco, ipaddress.IPv6Address) and endereco.ipv4_mapped is not None:
        endereco = endereco.ipv4_mapped
    if any(endereco in rede for rede in _REDES_BLOQUEADAS):
        return False
    return endereco.is_global


def _e_ip_literal(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
    except ValueError:
        return False
    return True


class ClienteHttpSeguro:
    """Busca páginas por HTTP GET recusando destinos internos e limitando o consumo."""

    def __init__(
        self,
        timeout_segundos: float = 15.0,
        max_redirecionamentos: int = 5,
        max_bytes: int = 2 * 1024 * 1024,
        resolvedor: Callable[[str], Sequence[str]] = _resolver_dns,
        transporte: Optional[httpx.BaseTransport] = None,
        relogio: Callable[[], float] = time.monotonic,
    ) -> None:
        self._timeout_segundos = timeout_segundos
        self._max_redirecionamentos = max_redirecionamentos
        self._max_bytes = max_bytes
        self._resolvedor = resolvedor
        self._transporte = transporte
        self._relogio = relogio

    def obter(self, url: str, cabecalhos: Optional[Mapping[str, str]] = None) -> RespostaHttp:
        inicio = self._relogio()
        atual = url
        with httpx.Client(
            transport=self._transporte,
            timeout=httpx.Timeout(self._timeout_segundos),
            follow_redirects=False,
        ) as cliente:
            for salto in range(self._max_redirecionamentos + 1):
                self._verificar_prazo(inicio)
                resultado = self._requisitar(cliente, atual, cabecalhos or {}, inicio)
                if isinstance(resultado, RespostaHttp):
                    return resultado
                if salto == self._max_redirecionamentos:
                    break
                atual = urljoin(atual, resultado.destino)
        raise RequisicaoHttpRecusada(MotivoFalhaHttp.EXCESSO_REDIRECIONAMENTOS)

    def _requisitar(
        self,
        cliente: httpx.Client,
        url: str,
        cabecalhos: Mapping[str, str],
        inicio: float,
    ) -> RespostaHttp | _Redirecionamento:
        url_fixada, host_cabecalho, sni = self._validar_e_fixar(url)
        headers = {"User-Agent": _USER_AGENT, **cabecalhos, "Host": host_cabecalho}
        extensoes = {"sni_hostname": sni} if sni else {}
        try:
            with cliente.stream("GET", url_fixada, headers=headers, extensions=extensoes) as resposta:
                destino = resposta.headers.get("location")
                if resposta.status_code in _CODIGOS_DE_REDIRECIONAMENTO and destino:
                    return _Redirecionamento(destino=destino)
                texto = self._ler_corpo(resposta, inicio)
                return RespostaHttp(status=resposta.status_code, texto=texto, url_final=url)
        except httpx.TimeoutException as erro:
            raise RequisicaoHttpRecusada(MotivoFalhaHttp.TEMPO_ESGOTADO, str(erro)) from erro
        except httpx.HTTPError as erro:
            raise RequisicaoHttpRecusada(MotivoFalhaHttp.FALHA_DE_REDE, str(erro)) from erro

    def _validar_e_fixar(self, url: str) -> tuple[str, str, Optional[str]]:
        partes = urlsplit(url)
        host = partes.hostname
        if partes.scheme.lower() not in _ESQUEMAS_ACEITOS or not host:
            raise RequisicaoHttpRecusada(MotivoFalhaHttp.ENDERECO_RECUSADO, "esquema ou host inválido")
        if partes.username is not None or partes.password is not None:
            raise RequisicaoHttpRecusada(MotivoFalhaHttp.ENDERECO_RECUSADO, "credenciais na URL")
        try:
            porta = partes.port
        except ValueError as erro:
            raise RequisicaoHttpRecusada(MotivoFalhaHttp.ENDERECO_RECUSADO, "porta inválida") from erro

        ip = self._escolher_ip_publico(host)
        ip_na_url = f"[{ip}]" if ":" in ip else ip
        host_na_url = f"[{host}]" if ":" in host else host
        sufixo_porta = f":{porta}" if porta else ""
        url_fixada = urlunsplit(
            (partes.scheme.lower(), f"{ip_na_url}{sufixo_porta}", partes.path or "/", partes.query, "")
        )
        sni = host if partes.scheme.lower() == "https" else None
        return url_fixada, f"{host_na_url}{sufixo_porta}", sni

    def _escolher_ip_publico(self, host: str) -> str:
        if _e_ip_literal(host):
            enderecos: Sequence[str] = [host]
        else:
            try:
                enderecos = self._resolvedor(host)
            except OSError as erro:
                raise RequisicaoHttpRecusada(MotivoFalhaHttp.FALHA_DE_REDE, "falha ao resolver o DNS") from erro
        if not enderecos:
            raise RequisicaoHttpRecusada(MotivoFalhaHttp.FALHA_DE_REDE, "host sem endereço")
        if not all(_ip_publico(endereco) for endereco in enderecos):
            raise RequisicaoHttpRecusada(MotivoFalhaHttp.ENDERECO_RECUSADO, "endereço não público")
        return enderecos[0]

    def _ler_corpo(self, resposta: httpx.Response, inicio: float) -> str:
        tamanho_informado = resposta.headers.get("content-length")
        if tamanho_informado and tamanho_informado.isdigit() and int(tamanho_informado) > self._max_bytes:
            raise RequisicaoHttpRecusada(MotivoFalhaHttp.TAMANHO_EXCEDIDO)
        conteudo = bytearray()
        for bloco in resposta.iter_bytes():
            self._verificar_prazo(inicio)
            conteudo += bloco
            if len(conteudo) > self._max_bytes:
                raise RequisicaoHttpRecusada(MotivoFalhaHttp.TAMANHO_EXCEDIDO)
        return self._decodificar(bytes(conteudo), resposta.charset_encoding)

    @staticmethod
    def _decodificar(conteudo: bytes, charset: Optional[str]) -> str:
        try:
            return conteudo.decode(charset or "utf-8", errors="replace")
        except LookupError:
            return conteudo.decode("utf-8", errors="replace")

    def _verificar_prazo(self, inicio: float) -> None:
        if self._relogio() - inicio > self._timeout_segundos:
            raise RequisicaoHttpRecusada(MotivoFalhaHttp.TEMPO_ESGOTADO)
