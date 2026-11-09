"""Trechos de prompt comuns aos adapters de IA que recebem um ContextoVaga."""
from __future__ import annotations

from jobsync.curriculo.domain.contexto_vaga import ContextoVaga


def linha_cargo_alvo(contexto: ContextoVaga) -> str:
    """Linha com o cargo-alvo, seguida de linha em branco; vazia quando não há cargo-alvo."""
    if not contexto.cargo_alvo:
        return ""
    return f"Cargo-alvo (título da vaga): {contexto.cargo_alvo}\n\n"
