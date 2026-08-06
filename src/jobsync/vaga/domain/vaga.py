"""Entidade de domínio para uma vaga capturada."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class Vaga:
    """Vaga capturada (via extensão de navegador ou colada manualmente) e associada a um perfil."""

    id: str
    perfil_identificador: str
    texto_descricao: str
    data_captura: datetime
    url_origem: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.id or not self.id.strip():
            raise ValueError("O id da vaga não pode ser vazio.")
        if not self.perfil_identificador or not self.perfil_identificador.strip():
            raise ValueError("O identificador do perfil não pode ser vazio.")
        if not self.texto_descricao or not self.texto_descricao.strip():
            raise ValueError("O texto da descrição da vaga não pode ser vazio.")
