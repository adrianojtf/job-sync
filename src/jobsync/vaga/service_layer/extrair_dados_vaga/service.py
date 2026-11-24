"""Caso de uso: ler os dados de uma vaga a partir do link ou do texto, como rascunho.

Nada é persistido. O texto informado tem prioridade sobre o link. O limite de
leituras só é consumido quando há leitura de link ou chamada à IA, depois de a
entrada e o link terem sido validados.
"""
from __future__ import annotations

import dataclasses
import logging
import time
from typing import Mapping, Optional
from urllib.parse import urlsplit

from jobsync.vaga.domain.dados_vaga import DadosVaga
from jobsync.vaga.domain.exceptions import (
    FonteVagaNaoSuportada,
    LeituraVagaIndisponivel,
    LimiteLeituraVagaExcedido,
    LinkVagaInvalido,
)
from jobsync.vaga.domain.extrator_dados_vaga_de_texto_port import ExtratorDadosVagaDeTextoPort
from jobsync.vaga.domain.leitor_vaga_por_link_port import LeitorVagaPorLinkPort
from jobsync.vaga.domain.limitador_leitura_vaga_port import LimitadorLeituraVagaPort
from jobsync.vaga.domain.link_vaga import FonteVaga, LinkVaga
from jobsync.vaga.service_layer.extrair_dados_vaga.dtos import ExtrairDadosVagaInputDto
from jobsync.vaga.service_layer.extrair_dados_vaga.validator import ExtrairDadosVagaInputValidator

logger = logging.getLogger(__name__)

_FONTE_TEXTO = "texto"


class ExtrairDadosVaga:
    """Devolve o rascunho dos dados de uma vaga, lido do link ou extraído do texto."""

    def __init__(
        self,
        leitores: Mapping[FonteVaga, LeitorVagaPorLinkPort],
        extrator_texto: ExtratorDadosVagaDeTextoPort,
        limitador: LimitadorLeituraVagaPort,
        linkedin_habilitado: bool = True,
    ) -> None:
        self._leitores = leitores
        self._extrator_texto = extrator_texto
        self._limitador = limitador
        self._linkedin_habilitado = linkedin_habilitado

    def executar(self, input_dto: ExtrairDadosVagaInputDto) -> DadosVaga:
        ExtrairDadosVagaInputValidator.validar(input_dto)
        if input_dto.texto and input_dto.texto.strip():
            return self._extrair_do_texto(input_dto)
        return self._ler_do_link(input_dto)

    def _extrair_do_texto(self, input_dto: ExtrairDadosVagaInputDto) -> DadosVaga:
        url = self._url_normalizada_ou_none(input_dto.url)
        self._consumir_limite(input_dto.usuario_id)

        inicio = time.perf_counter()
        dados = self._extrator_texto.extrair(input_dto.texto)
        if url and not dados.url:
            dados = dataclasses.replace(dados, url=url)
        self._registrar_conclusao(_FONTE_TEXTO, None, inicio, dados)
        return dados

    def _ler_do_link(self, input_dto: ExtrairDadosVagaInputDto) -> DadosVaga:
        link = LinkVaga.criar(input_dto.url)
        leitor = self._escolher_leitor(link)
        self._consumir_limite(input_dto.usuario_id)

        inicio = time.perf_counter()
        try:
            dados = leitor.ler(link)
        except LeituraVagaIndisponivel as erro:
            logger.warning(
                "Leitura de vaga indisponível: fonte=%s dominio=%s motivo=%s",
                link.fonte.value,
                self._dominio(link.url),
                erro.motivo.value,
            )
            raise
        dados = dataclasses.replace(dados, url=link.url)
        self._registrar_conclusao(link.fonte.value, link.url, inicio, dados)
        return dados

    def _escolher_leitor(self, link: LinkVaga) -> LeitorVagaPorLinkPort:
        if link.fonte is FonteVaga.LINKEDIN and not self._linkedin_habilitado:
            raise FonteVagaNaoSuportada(
                "A leitura de links do LinkedIn está desativada. Cole o texto da vaga para continuar."
            )
        leitor = self._leitores.get(link.fonte)
        if leitor is None:
            raise FonteVagaNaoSuportada("Este tipo de link não é suportado. Cole o texto da vaga para continuar.")
        return leitor

    def _consumir_limite(self, usuario_id: str) -> None:
        try:
            self._limitador.registrar(usuario_id)
        except LimiteLeituraVagaExcedido:
            logger.warning("Limite de leituras de vaga excedido: usuario=%s", usuario_id)
            raise

    @staticmethod
    def _url_normalizada_ou_none(url: Optional[str]) -> Optional[str]:
        if not url or not url.strip():
            return None
        try:
            return LinkVaga.criar(url).url
        except LinkVagaInvalido:
            return None

    @staticmethod
    def _dominio(url: Optional[str]) -> str:
        return (urlsplit(url).hostname or "") if url else ""

    def _registrar_conclusao(self, fonte: str, url: Optional[str], inicio: float, dados: DadosVaga) -> None:
        campos = [campo.name for campo in dataclasses.fields(dados) if getattr(dados, campo.name) is not None]
        logger.info(
            "Vaga lida: fonte=%s dominio=%s duracao_ms=%d campos=%s",
            fonte,
            self._dominio(url),
            int((time.perf_counter() - inicio) * 1000),
            ",".join(campos),
        )
