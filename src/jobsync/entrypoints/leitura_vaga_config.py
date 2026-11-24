"""Leitura da configuração da leitura de vagas por link a partir das variáveis de ambiente (VAGA_LEITURA_*)."""
from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass

_FALSOS = {"0", "false", "no", "off"}


@dataclass(frozen=True)
class ConfiguracaoLeituraVaga:
    """Opções da leitura de vagas: fonte do LinkedIn, limites de uso por pessoa e tempo máximo."""

    linkedin_habilitado: bool = True
    limite_por_minuto: int = 10
    limite_por_dia: int = 100
    timeout_segundos: float = 15.0


_PADRAO = ConfiguracaoLeituraVaga()


def _habilitado(valor: str | None) -> bool:
    return (valor or "").strip().lower() not in _FALSOS


def _inteiro_positivo(valor: str | None, padrao: int) -> int:
    try:
        numero = int((valor or "").strip())
    except ValueError:
        return padrao
    return numero if numero > 0 else padrao


def _decimal_positivo(valor: str | None, padrao: float) -> float:
    try:
        numero = float((valor or "").strip())
    except ValueError:
        return padrao
    return numero if math.isfinite(numero) and numero > 0 else padrao


def configuracao_leitura_vaga_do_ambiente(ambiente: Mapping[str, str]) -> ConfiguracaoLeituraVaga:
    return ConfiguracaoLeituraVaga(
        linkedin_habilitado=_habilitado(ambiente.get("VAGA_LEITURA_LINKEDIN_HABILITADA")),
        limite_por_minuto=_inteiro_positivo(ambiente.get("VAGA_LEITURA_LIMITE_POR_MINUTO"), _PADRAO.limite_por_minuto),
        limite_por_dia=_inteiro_positivo(ambiente.get("VAGA_LEITURA_LIMITE_POR_DIA"), _PADRAO.limite_por_dia),
        timeout_segundos=_decimal_positivo(ambiente.get("VAGA_LEITURA_TIMEOUT_SEGUNDOS"), _PADRAO.timeout_segundos),
    )
