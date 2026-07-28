"""Schema e conexão SQLite compartilhados pelos *RepositoryImpl.

Cada RepositoryImpl abre sua própria conexão para o mesmo arquivo
(`storage/job_sync.db`) e roda este mesmo script de schema (idempotente,
`CREATE TABLE IF NOT EXISTS`), garantindo que todas as tabelas existam
independentemente da ordem de instanciação. Os RepositoryImpl são
implementados como classes separadas (uma por Repository) em vez de uma
única classe implementando todas as portas, porque `CurriculoSalvoRepository`,
`VagaRepository` e `CandidaturaRepository` declaram métodos com o mesmo nome
(`salvar`, `listar_por_perfil`) para tipos de domínio diferentes — Python não
suporta sobrecarga por tipo de parâmetro, então uma única classe quebraria
silenciosamente o contrato de uma das portas.
"""
from __future__ import annotations

import sqlite3

_SCHEMA = """
CREATE TABLE IF NOT EXISTS perfil (
    identificador TEXT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS curriculo_salvo (
    id TEXT PRIMARY KEY,
    perfil_identificador TEXT NOT NULL REFERENCES perfil(identificador),
    nome_referencia TEXT NOT NULL,
    pdf_bytes BLOB NOT NULL,
    data_upload TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS token_captura (
    token TEXT PRIMARY KEY,
    perfil_identificador TEXT NOT NULL REFERENCES perfil(identificador)
);

CREATE TABLE IF NOT EXISTS vaga (
    id TEXT PRIMARY KEY,
    perfil_identificador TEXT NOT NULL REFERENCES perfil(identificador),
    texto_descricao TEXT NOT NULL,
    url_origem TEXT,
    data_captura TEXT NOT NULL,
    convertida_em_candidatura INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS candidatura (
    id TEXT PRIMARY KEY,
    perfil_identificador TEXT NOT NULL REFERENCES perfil(identificador),
    vaga_id TEXT REFERENCES vaga(id),
    curriculo_salvo_id TEXT REFERENCES curriculo_salvo(id),
    empresa TEXT NOT NULL,
    cargo TEXT NOT NULL,
    status TEXT NOT NULL,
    data_aplicacao TEXT NOT NULL,
    data_ultima_mudanca_status TEXT NOT NULL
);
"""


def criar_conexao(caminho_banco: str) -> sqlite3.Connection:
    """Abre uma conexão SQLite e garante que o schema completo já exista."""
    conexao = sqlite3.connect(caminho_banco, check_same_thread=False)
    conexao.executescript(_SCHEMA)
    conexao.commit()
    return conexao
