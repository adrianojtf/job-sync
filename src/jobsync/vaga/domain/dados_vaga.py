"""Value Object com os dados lidos de uma vaga, ainda como rascunho."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Optional

_LIMITE_DESCRICAO = 50_000
_LIMITE_URL = 2048
_LIMITE_CAMPO_CURTO = 200


@dataclass(frozen=True)
class DadosVaga:
    """Dados de uma vaga lidos de um link ou de um texto; a descrição é o texto original."""

    descricao: str
    cargo: Optional[str] = None
    empresa: Optional[str] = None
    local: Optional[str] = None
    url: Optional[str] = None
    tipo_contratacao: Optional[str] = None
    senioridade: Optional[str] = None
    setor: Optional[str] = None

    def __post_init__(self) -> None:
        for campo in fields(self):
            valor = getattr(self, campo.name)
            if valor is not None:
                limpo = valor.strip()
                object.__setattr__(self, campo.name, limpo or None)

        if self.descricao is None:
            raise ValueError("A descrição da vaga não pode ser vazia.")
        self._validar_tamanho("descricao", _LIMITE_DESCRICAO)
        self._validar_tamanho("url", _LIMITE_URL)
        for nome in ("cargo", "empresa", "local", "tipo_contratacao", "senioridade", "setor"):
            self._validar_tamanho(nome, _LIMITE_CAMPO_CURTO)

    def _validar_tamanho(self, nome: str, limite: int) -> None:
        valor = getattr(self, nome)
        if valor is not None and len(valor) > limite:
            raise ValueError(f"O campo '{nome}' excede o tamanho máximo de {limite} caracteres.")
