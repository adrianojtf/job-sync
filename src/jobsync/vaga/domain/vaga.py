"""Entidade de domínio para uma vaga capturada."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

_CAMPOS_DE_IDENTIFICACAO = ("cargo", "empresa", "local")
_LIMITE_CAMPO_DE_IDENTIFICACAO = 200


@dataclass(frozen=True)
class Vaga:
    """Vaga capturada (via extensão, link ou colada manualmente) e associada a um perfil.

    `cargo`, `empresa` e `local` são opcionais: aparecem quando foram lidos do link ou do texto.
    """

    id: str
    perfil_identificador: str
    texto_descricao: str
    data_captura: datetime
    url_origem: Optional[str] = None
    cargo: Optional[str] = None
    empresa: Optional[str] = None
    local: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.id or not self.id.strip():
            raise ValueError("O id da vaga não pode ser vazio.")
        if not self.perfil_identificador or not self.perfil_identificador.strip():
            raise ValueError("O identificador do perfil não pode ser vazio.")
        if not self.texto_descricao or not self.texto_descricao.strip():
            raise ValueError("O texto da descrição da vaga não pode ser vazio.")
        for nome in _CAMPOS_DE_IDENTIFICACAO:
            valor = getattr(self, nome)
            if valor is None:
                continue
            limpo = valor.strip() or None
            if limpo is not None and len(limpo) > _LIMITE_CAMPO_DE_IDENTIFICACAO:
                raise ValueError(
                    f"O campo '{nome}' excede o tamanho máximo de {_LIMITE_CAMPO_DE_IDENTIFICACAO} caracteres."
                )
            object.__setattr__(self, nome, limpo)
