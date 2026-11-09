"""Trechos de prompt comuns aos adapters de IA que recebem um ContextoVaga."""
from __future__ import annotations

from jobsync.curriculo.domain.contexto_vaga import ContextoVaga


def linha_cargo_alvo(contexto: ContextoVaga) -> str:
    """Linha com o cargo-alvo, seguida de linha em branco; vazia quando não há cargo-alvo."""
    if not contexto.cargo_alvo:
        return ""
    return f"Cargo-alvo (título da vaga): {contexto.cargo_alvo}\n\n"


REGRA_RESPONSABILIDADES_IMPLICITAS = (
    "Se a vaga pedir uma responsabilidade essencial da vaga que seja comum ao cargo desta "
    "experiência (ex.: code review para um desenvolvedor, gestão de backlog para um PO) e ela "
    "não estiver no texto, cite-a em uma conquista ou no contexto. Não cite responsabilidades "
    "atípicas para o cargo exercido e não invente métricas para elas."
)
"""Regra genérica (JOB-0037): o que é implícito ao cargo exercido pode aparecer no currículo."""
