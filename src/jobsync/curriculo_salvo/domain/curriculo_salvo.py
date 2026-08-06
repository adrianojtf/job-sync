"""Entidade de domínio para um currículo (PDF) salvo na biblioteca de um perfil.

Distinta de `jobsync.curriculo.domain.Curriculo`, que representa o currículo já
extraído/estruturado em seções. `CurriculoSalvo` é o artefato bruto (PDF) que
o usuário guarda para reutilizar em futuras adaptações, sem exigir novo upload.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CurriculoSalvo:
    """PDF de currículo salvo na biblioteca de um perfil."""

    id: str
    perfil_identificador: str
    nome_referencia: str
    pdf_bytes: bytes
    data_upload: datetime

    def __post_init__(self) -> None:
        if not self.id or not self.id.strip():
            raise ValueError("O id do currículo salvo não pode ser vazio.")
        if not self.perfil_identificador or not self.perfil_identificador.strip():
            raise ValueError("O identificador do perfil não pode ser vazio.")
        if not self.nome_referencia or not self.nome_referencia.strip():
            raise ValueError("O nome de referência do currículo não pode ser vazio.")
        if not self.pdf_bytes:
            raise ValueError("O conteúdo do PDF do currículo não pode ser vazio.")
