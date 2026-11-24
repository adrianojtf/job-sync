"""Tradução de status e falhas HTTP em motivos de leitura de vaga indisponível."""
from __future__ import annotations

from jobsync.shared_kernel.adapters.cliente_http_seguro import MotivoFalhaHttp
from jobsync.vaga.domain.exceptions import MotivoLeituraIndisponivel

_STATUS_DE_BLOQUEIO = frozenset({401, 403, 429, 451})
_STATUS_DE_VAGA_INEXISTENTE = frozenset({404, 410})

_MOTIVO_POR_FALHA_HTTP = {
    MotivoFalhaHttp.ENDERECO_RECUSADO: MotivoLeituraIndisponivel.ENDERECO_RECUSADO,
    MotivoFalhaHttp.TEMPO_ESGOTADO: MotivoLeituraIndisponivel.TEMPO_ESGOTADO,
    MotivoFalhaHttp.FALHA_DE_REDE: MotivoLeituraIndisponivel.FALHA_DE_REDE,
    MotivoFalhaHttp.EXCESSO_REDIRECIONAMENTOS: MotivoLeituraIndisponivel.FALHA_DE_REDE,
    MotivoFalhaHttp.TAMANHO_EXCEDIDO: MotivoLeituraIndisponivel.SEM_DADOS,
}


def motivo_por_status_http(status: int) -> MotivoLeituraIndisponivel:
    if status in _STATUS_DE_BLOQUEIO:
        return MotivoLeituraIndisponivel.BLOQUEADA
    if status in _STATUS_DE_VAGA_INEXISTENTE:
        return MotivoLeituraIndisponivel.NAO_ENCONTRADA
    if status >= 500:
        return MotivoLeituraIndisponivel.FALHA_DE_REDE
    return MotivoLeituraIndisponivel.SEM_DADOS


def motivo_por_falha_http(falha: MotivoFalhaHttp) -> MotivoLeituraIndisponivel:
    return _MOTIVO_POR_FALHA_HTTP[falha]
