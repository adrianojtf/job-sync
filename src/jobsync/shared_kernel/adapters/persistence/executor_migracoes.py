"""Aplica as migrações SQL versionadas de `migracoes/` (arquivos `NNNN_descricao.sql`).

O executor não faz commit: roda dentro da transação da conexão recebida, e o
DDL do PostgreSQL é transacional. Quem chama decide confirmar ou reverter.
"""
from __future__ import annotations

import logging
from pathlib import Path

from psycopg import Connection

logger = logging.getLogger(__name__)

DIRETORIO_MIGRACOES = Path(__file__).resolve().parent / "migracoes"
_CHAVE_TRAVA = 727274


def executar_migracoes(conexao: Connection, diretorio: Path = DIRETORIO_MIGRACOES) -> list[str]:
    """Aplica as migrações pendentes em ordem e devolve as versões aplicadas agora."""
    conexao.execute("SELECT pg_advisory_xact_lock(%s)", (_CHAVE_TRAVA,))
    conexao.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            versao TEXT PRIMARY KEY,
            aplicada_em TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
    ja_aplicadas = {linha[0] for linha in conexao.execute("SELECT versao FROM schema_migrations").fetchall()}

    aplicadas: list[str] = []
    for arquivo in sorted(diretorio.glob("*.sql")):
        if arquivo.stem in ja_aplicadas:
            continue
        conexao.execute(arquivo.read_text(encoding="utf-8"))
        conexao.execute("INSERT INTO schema_migrations (versao) VALUES (%s)", (arquivo.stem,))
        aplicadas.append(arquivo.stem)
        logger.info("Migração aplicada: %s", arquivo.stem)
    return aplicadas
