"""Migração dos dados do arquivo SQLite antigo para o PostgreSQL.

Regras: o SQLite é aberto somente para leitura; a origem é validada antes de
qualquer escrita; tudo é gravado em uma única transação e conferido (contagens,
hash dos PDFs e posições do board) antes do commit. Qualquer divergência reverte.
O arquivo SQLite nunca é alterado e serve de backup.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from psycopg import Connection
from psycopg.types.json import Jsonb

from jobsync.shared_kernel.adapters.persistence.executor_migracoes import executar_migracoes

TABELAS_EM_ORDEM = (
    "perfil",
    "curriculo_salvo",
    "token_captura",
    "vaga",
    "candidatura",
    "perfil_estruturado",
)

_COLUNAS_JSON = (
    "experiencias_json",
    "formacoes_json",
    "certificacoes_json",
    "idiomas_json",
    "tecnologias_json",
)
_TAMANHO_LOTE = 500


class OrigemInvalida(Exception):
    def __init__(self, problemas: list[str]) -> None:
        super().__init__("; ".join(problemas))
        self.problemas = problemas


class DestinoInvalido(Exception):
    pass


class ValidacaoFalhou(Exception):
    def __init__(self, divergencias: list[str]) -> None:
        super().__init__("; ".join(divergencias))
        self.divergencias = divergencias


@dataclass(frozen=True)
class LinhaRelatorio:
    tabela: str
    lidos: int
    gravados: int


@dataclass(frozen=True)
class Relatorio:
    linhas: tuple[LinhaRelatorio, ...]
    pdfs_conferidos: int
    simulacao: bool
    migracoes_aplicadas: tuple[str, ...] = field(default_factory=tuple)


def converter_data(texto: str, fuso_origem: ZoneInfo | None) -> datetime:
    """Interpreta a data ISO sem fuso do SQLite no fuso informado (ou no fuso local da máquina)."""
    data = datetime.fromisoformat(texto)
    if data.tzinfo is not None:
        return data.astimezone(timezone.utc)
    data = data.replace(tzinfo=fuso_origem) if fuso_origem else data.astimezone()
    return data.astimezone(timezone.utc)


def hash_pdf(conteudo: bytes) -> str:
    return hashlib.sha256(conteudo).hexdigest()


def abrir_sqlite_somente_leitura(caminho: Path) -> sqlite3.Connection:
    if not caminho.is_file():
        raise OrigemInvalida([f"Arquivo SQLite não encontrado: {caminho}"])
    return sqlite3.connect(f"file:{caminho.resolve()}?mode=ro", uri=True)


def verificar_origem(origem: sqlite3.Connection, fuso_origem: ZoneInfo | None) -> None:
    """Reúne todos os problemas da origem de uma vez e aborta se houver algum."""
    problemas: list[str] = []
    existentes = {l[0] for l in origem.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    ausentes = [t for t in TABELAS_EM_ORDEM if t not in existentes]
    if ausentes:
        raise OrigemInvalida([f"Tabelas ausentes no SQLite: {', '.join(ausentes)}"])

    colunas_candidatura = {l[1] for l in origem.execute("PRAGMA table_info(candidatura)")}
    if "posicao" not in colunas_candidatura:
        raise OrigemInvalida(
            [
                "A tabela candidatura não tem a coluna posicao (banco antigo). "
                "Abra uma vez o banco com a versão anterior do sistema, que cria a coluna, e repita."
            ]
        )

    for tabela, linha_id, filha, pai in origem.execute("PRAGMA foreign_key_check"):
        problemas.append(f"Referência órfã: {tabela} (rowid {linha_id}) aponta para {filha} inexistente ({pai})")

    for tabela, coluna in (
        ("curriculo_salvo", "data_upload"),
        ("vaga", "data_captura"),
        ("candidatura", "data_aplicacao"),
        ("candidatura", "data_ultima_mudanca_status"),
    ):
        for id_, valor in origem.execute(f"SELECT rowid, {coluna} FROM {tabela}"):
            try:
                converter_data(valor, fuso_origem)
            except (ValueError, TypeError):
                problemas.append(f"Data inválida em {tabela}.{coluna} (rowid {id_}): {valor!r}")

    for coluna in _COLUNAS_JSON:
        for id_, valor in origem.execute(f"SELECT rowid, {coluna} FROM perfil_estruturado"):
            try:
                json.loads(valor)
            except (ValueError, TypeError):
                problemas.append(f"JSON inválido em perfil_estruturado.{coluna} (rowid {id_})")

    if problemas:
        raise OrigemInvalida(problemas)


def verificar_destino_vazio(destino: Connection) -> None:
    com_dados = [
        tabela for tabela in TABELAS_EM_ORDEM if destino.execute(f"SELECT 1 FROM {tabela} LIMIT 1").fetchone()
    ]
    if com_dados:
        raise DestinoInvalido(
            f"O destino já tem dados em: {', '.join(com_dados)}. A migração só roda em um banco vazio."
        )


def _lotes(linhas: list[tuple]):
    for inicio in range(0, len(linhas), _TAMANHO_LOTE):
        yield linhas[inicio : inicio + _TAMANHO_LOTE]


def _copiar(destino: Connection, tabela: str, colunas: str, linhas: list[tuple]) -> None:
    marcadores = ", ".join(["%s"] * len(colunas.split(",")))
    with destino.cursor() as cursor:
        for lote in _lotes(linhas):
            cursor.executemany(f"INSERT INTO {tabela} ({colunas}) VALUES ({marcadores})", lote)


def _ler(origem: sqlite3.Connection, tabela: str, colunas: str) -> list[tuple]:
    return origem.execute(f"SELECT {colunas} FROM {tabela} ORDER BY rowid").fetchall()


def _copiar_tabelas(origem: sqlite3.Connection, destino: Connection, fuso: ZoneInfo | None) -> dict[str, int]:
    lidos: dict[str, int] = {}

    linhas = _ler(origem, "perfil", "identificador")
    lidos["perfil"] = len(linhas)
    _copiar(destino, "perfil", "identificador", linhas)

    cols = "id, perfil_identificador, nome_referencia, pdf_bytes, data_upload"
    linhas = [(a, b, c, d, converter_data(e, fuso)) for a, b, c, d, e in _ler(origem, "curriculo_salvo", cols)]
    lidos["curriculo_salvo"] = len(linhas)
    _copiar(destino, "curriculo_salvo", cols, linhas)

    linhas = _ler(origem, "token_captura", "token, perfil_identificador")
    lidos["token_captura"] = len(linhas)
    _copiar(destino, "token_captura", "token, perfil_identificador", linhas)

    cols = "id, perfil_identificador, texto_descricao, url_origem, data_captura, convertida_em_candidatura"
    linhas = [
        (a, b, c, d, converter_data(e, fuso), bool(f)) for a, b, c, d, e, f in _ler(origem, "vaga", cols)
    ]
    lidos["vaga"] = len(linhas)
    _copiar(destino, "vaga", cols, linhas)

    cols = (
        "id, perfil_identificador, vaga_id, curriculo_salvo_id, empresa, cargo, status, "
        "data_aplicacao, data_ultima_mudanca_status, posicao"
    )
    linhas = [
        (i, p, v, c, e, g, s, converter_data(da, fuso), converter_data(du, fuso), pos)
        for i, p, v, c, e, g, s, da, du, pos in _ler(origem, "candidatura", cols)
    ]
    lidos["candidatura"] = len(linhas)
    _copiar(destino, "candidatura", cols, linhas)

    cols = (
        "perfil_identificador, nome_completo, email, linkedin, resumo_profissional, "
        + ", ".join(_COLUNAS_JSON)
    )
    linhas = [
        (*linha[:5], *(Jsonb(json.loads(valor)) for valor in linha[5:]))
        for linha in _ler(origem, "perfil_estruturado", cols)
    ]
    lidos["perfil_estruturado"] = len(linhas)
    _copiar(destino, "perfil_estruturado", cols, linhas)
    return lidos


def _validar(origem: sqlite3.Connection, destino: Connection, lidos: dict[str, int]) -> int:
    divergencias: list[str] = []
    for tabela in TABELAS_EM_ORDEM:
        gravados = destino.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0]
        if gravados != lidos[tabela]:
            divergencias.append(f"{tabela}: {lidos[tabela]} lidos, {gravados} gravados")

    hashes_origem = {id_: hash_pdf(pdf) for id_, pdf in origem.execute("SELECT id, pdf_bytes FROM curriculo_salvo")}
    hashes_destino = {
        id_: hash_pdf(bytes(pdf)) for id_, pdf in destino.execute("SELECT id, pdf_bytes FROM curriculo_salvo")
    }
    if hashes_origem != hashes_destino:
        divergencias.append("curriculo_salvo: o conteúdo de algum PDF difere entre origem e destino")

    posicoes_origem = sorted(origem.execute("SELECT id, status, posicao FROM candidatura").fetchall())
    posicoes_destino = sorted(destino.execute("SELECT id, status, posicao FROM candidatura").fetchall())
    if posicoes_origem != posicoes_destino:
        divergencias.append("candidatura: a ordem dos cartões difere entre origem e destino")

    if divergencias:
        raise ValidacaoFalhou(divergencias)
    return len(hashes_origem)


def migrar(
    caminho_sqlite: Path,
    destino: Connection,
    *,
    simulacao: bool = False,
    fuso_origem: ZoneInfo | None = None,
) -> Relatorio:
    """Copia tudo do SQLite para o PostgreSQL em uma transação; `simulacao` reverte no final."""
    origem = abrir_sqlite_somente_leitura(caminho_sqlite)
    try:
        verificar_origem(origem, fuso_origem)
        try:
            aplicadas = executar_migracoes(destino)
            verificar_destino_vazio(destino)
            lidos = _copiar_tabelas(origem, destino, fuso_origem)
            pdfs = _validar(origem, destino, lidos)
        except BaseException:
            destino.rollback()
            raise
        if simulacao:
            destino.rollback()
        else:
            destino.commit()
        return Relatorio(
            linhas=tuple(LinhaRelatorio(t, lidos[t], lidos[t]) for t in TABELAS_EM_ORDEM),
            pdfs_conferidos=pdfs,
            simulacao=simulacao,
            migracoes_aplicadas=tuple(aplicadas),
        )
    finally:
        origem.close()
