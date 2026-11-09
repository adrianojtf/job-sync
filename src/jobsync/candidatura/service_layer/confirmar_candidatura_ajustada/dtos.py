"""DTO de input para o caso de uso ConfirmarCandidaturaAjustada."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ConfirmarCandidaturaAjustadaInputDto:
    """Dados da vaga e o PDF gerado na tela de ajuste, para registrar a candidatura."""

    perfil_identificador: str
    cargo: str
    empresa: str
    descricao_vaga: str
    nome_arquivo: str
    pdf_bytes: bytes
