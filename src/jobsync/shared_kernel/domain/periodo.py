"""Value Object: período de uma experiência ou formação, em texto como o usuário digita.

Formato aceito: `início - fim`, em que cada lado é `aaaa`, `mmm aaaa` (mês abreviado ou por
extenso, em português ou inglês) ou `mm/aaaa`, e o fim também pode ser `Atual`, `Presente`,
`Present` ou `Current`. O separador é hífen ou travessão, com ou sem espaços. Uma data só vale
como início e fim iguais. O início não pode ser depois do fim.

A leitura é usada na validação de entrada; as entidades guardam o texto como foi digitado.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from jobsync.shared_kernel.domain.texto_normalizado import normalizar_texto

ANO_MINIMO = 1900
ANO_MAXIMO = 2100

_MESES = {
    "jan": 1, "fev": 2, "feb": 2, "mar": 3, "abr": 4, "apr": 4, "mai": 5, "may": 5, "jun": 6,
    "jul": 7, "ago": 8, "aug": 8, "set": 9, "sep": 9, "out": 10, "oct": 10, "nov": 11, "dez": 12, "dec": 12,
}
_ATUAL = frozenset({"atual", "presente", "present", "current"})
_SEPARADOR = re.compile(r"\s*[-–—]\s*")
_SO_ANO = re.compile(r"^(\d{4})$")
_MES_NUMERICO = re.compile(r"^(\d{2})/(\d{4})$")
_MES_POR_NOME = re.compile(r"^([^\W\d_]{3,})\.?\s+(\d{4})$")

MENSAGEM_DE_FORMATO = "Use o formato Mar 2024 - Atual ou 2020 - 2022."

Data = tuple[int, int | None]


class PeriodoInvalido(ValueError):
    """O texto não segue o formato de período."""

    def __init__(self, mensagem: str = MENSAGEM_DE_FORMATO) -> None:
        super().__init__(mensagem)


def _ano(texto: str) -> int:
    ano = int(texto)
    if not ANO_MINIMO <= ano <= ANO_MAXIMO:
        raise PeriodoInvalido(f"O ano deve estar entre {ANO_MINIMO} e {ANO_MAXIMO}. {MENSAGEM_DE_FORMATO}")
    return ano


def _ler_data(texto: str) -> Data:
    texto = texto.strip()
    if (m := _SO_ANO.match(texto)):
        return _ano(m.group(1)), None
    if (m := _MES_NUMERICO.match(texto)):
        mes = int(m.group(1))
        if not 1 <= mes <= 12:
            raise PeriodoInvalido()
        return _ano(m.group(2)), mes
    if (m := _MES_POR_NOME.match(texto)):
        mes = _MESES.get(normalizar_texto(m.group(1))[:3])
        if mes is None:
            raise PeriodoInvalido()
        return _ano(m.group(2)), mes
    raise PeriodoInvalido()


def _como_numero(data: Data) -> int:
    return data[0] * 13 + (data[1] or 0)


def validar_ano(texto: str) -> int:
    """Valida o ano de quatro dígitos de uma certificação e o devolve."""
    texto = texto.strip()
    if not _SO_ANO.match(texto):
        raise PeriodoInvalido("Use um ano com quatro dígitos, como 2023.")
    return _ano(texto)


@dataclass(frozen=True)
class Periodo:
    inicio: Data
    fim: Data | None
    """None quando o período segue em andamento."""

    @property
    def atual(self) -> bool:
        return self.fim is None

    @property
    def ano_inicial(self) -> int:
        return self.inicio[0]

    @classmethod
    def ler(cls, texto: str) -> Periodo:
        """Lê o período; levanta `PeriodoInvalido` se o texto não seguir o formato."""
        partes = _SEPARADOR.split(texto.strip())
        if len(partes) == 1:
            data = _ler_data(partes[0])
            return cls(inicio=data, fim=data)
        if len(partes) != 2 or not all(partes):
            raise PeriodoInvalido()
        inicio = _ler_data(partes[0])
        if normalizar_texto(partes[1]) in _ATUAL:
            return cls(inicio=inicio, fim=None)
        fim = _ler_data(partes[1])
        if _como_numero(inicio) > _como_numero(fim):
            raise PeriodoInvalido("O início não pode ser depois do fim. " + MENSAGEM_DE_FORMATO)
        return cls(inicio=inicio, fim=fim)
