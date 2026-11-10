"""Copia os dados do arquivo SQLite antigo para o PostgreSQL configurado em DATABASE_URL.

Uso:
    python -m jobsync.entrypoints.cli.migrar_sqlite_para_postgres --sqlite storage/job_sync.db [--dry-run]

Códigos de saída: 0 sucesso, 1 erro inesperado, 2 problemas na origem,
3 destino inválido, 4 divergência na validação.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import psycopg
from dotenv import load_dotenv

from jobsync.shared_kernel.adapters.persistence.conexao_postgres import (
    ErroConexaoBanco,
    descrever_destino,
    obter_url_banco,
)
from jobsync.shared_kernel.adapters.persistence.migracao_sqlite import (
    DestinoInvalido,
    OrigemInvalida,
    Relatorio,
    ValidacaoFalhou,
    migrar,
)

SUCESSO, ERRO_INESPERADO, ERRO_ORIGEM, ERRO_DESTINO, ERRO_VALIDACAO = 0, 1, 2, 3, 4


def _argumentos(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Migra os dados do SQLite para o PostgreSQL.")
    parser.add_argument("--sqlite", required=True, type=Path, help="Caminho do arquivo .db de origem")
    parser.add_argument("--dry-run", action="store_true", help="Executa e valida tudo, mas desfaz no final")
    parser.add_argument(
        "--fuso-origem",
        help="Fuso (ex.: America/Sao_Paulo) das datas antigas, que não guardavam fuso. "
        "Padrão: fuso local desta máquina.",
    )
    return parser.parse_args(argv)


def _formatar(relatorio: Relatorio) -> str:
    titulo = "SIMULAÇÃO (nada foi gravado)" if relatorio.simulacao else "MIGRAÇÃO CONCLUÍDA"
    linhas = [titulo, "", f"{'tabela':<20}{'lidos':>8}{'gravados':>10}"]
    linhas += [f"{l.tabela:<20}{l.lidos:>8}{l.gravados:>10}" for l in relatorio.linhas]
    linhas += ["", f"PDFs conferidos por hash: {relatorio.pdfs_conferidos}"]
    if relatorio.migracoes_aplicadas:
        linhas.append(f"Migrações de schema aplicadas: {', '.join(relatorio.migracoes_aplicadas)}")
    if relatorio.avisos:
        linhas += ["", "Avisos:", *[f"  - {aviso}" for aviso in relatorio.avisos]]
    return "\n".join(linhas)


def principal(argv: list[str] | None = None) -> int:
    load_dotenv()
    args = _argumentos(argv)
    try:
        fuso = ZoneInfo(args.fuso_origem) if args.fuso_origem else None
    except ZoneInfoNotFoundError:
        print(f"Fuso desconhecido: {args.fuso_origem}", file=sys.stderr)
        return ERRO_ORIGEM

    try:
        url = obter_url_banco()
        print(f"Destino: {descrever_destino(url)}")
        with psycopg.connect(url, options="-c TimeZone=UTC") as destino:
            relatorio = migrar(args.sqlite, destino, simulacao=args.dry_run, fuso_origem=fuso)
    except OrigemInvalida as erro:
        print("Problemas na origem (nada foi gravado):", file=sys.stderr)
        for problema in erro.problemas:
            print(f"  - {problema}", file=sys.stderr)
        return ERRO_ORIGEM
    except (DestinoInvalido, ErroConexaoBanco, psycopg.OperationalError) as erro:
        print(f"Destino inválido (nada foi gravado): {erro}", file=sys.stderr)
        return ERRO_DESTINO
    except ValidacaoFalhou as erro:
        print("A validação encontrou divergências e a migração foi desfeita:", file=sys.stderr)
        for divergencia in erro.divergencias:
            print(f"  - {divergencia}", file=sys.stderr)
        return ERRO_VALIDACAO

    print(_formatar(relatorio))
    return SUCESSO


if __name__ == "__main__":
    sys.exit(principal())
