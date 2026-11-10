"""Cria um arquivo SQLite no formato antigo do job-sync, para testar a migração de dados."""

import sqlite3

PDF_A = b"%PDF-1.4 \x00\xff\xfe curriculo A"
PDF_B = b"%PDF-1.4 curriculo B"

SCHEMA_ANTIGO = """
CREATE TABLE perfil (identificador TEXT PRIMARY KEY);
CREATE TABLE curriculo_salvo (
    id TEXT PRIMARY KEY, perfil_identificador TEXT NOT NULL REFERENCES perfil(identificador),
    nome_referencia TEXT NOT NULL, pdf_bytes BLOB NOT NULL, data_upload TEXT NOT NULL);
CREATE TABLE token_captura (
    token TEXT PRIMARY KEY, perfil_identificador TEXT NOT NULL REFERENCES perfil(identificador));
CREATE TABLE vaga (
    id TEXT PRIMARY KEY, perfil_identificador TEXT NOT NULL REFERENCES perfil(identificador),
    texto_descricao TEXT NOT NULL, url_origem TEXT, data_captura TEXT NOT NULL,
    convertida_em_candidatura INTEGER NOT NULL DEFAULT 0);
CREATE TABLE candidatura (
    id TEXT PRIMARY KEY, perfil_identificador TEXT NOT NULL REFERENCES perfil(identificador),
    vaga_id TEXT REFERENCES vaga(id), curriculo_salvo_id TEXT REFERENCES curriculo_salvo(id),
    empresa TEXT NOT NULL, cargo TEXT NOT NULL, status TEXT NOT NULL,
    data_aplicacao TEXT NOT NULL, data_ultima_mudanca_status TEXT NOT NULL,
    posicao INTEGER NOT NULL DEFAULT 0);
CREATE TABLE perfil_estruturado (
    perfil_identificador TEXT PRIMARY KEY REFERENCES perfil(identificador),
    nome_completo TEXT NOT NULL, email TEXT NOT NULL, linkedin TEXT NOT NULL DEFAULT '',
    resumo_profissional TEXT NOT NULL DEFAULT '', experiencias_json TEXT NOT NULL DEFAULT '[]',
    formacoes_json TEXT NOT NULL DEFAULT '[]', certificacoes_json TEXT NOT NULL DEFAULT '[]',
    idiomas_json TEXT NOT NULL DEFAULT '[]', tecnologias_json TEXT NOT NULL DEFAULT '[]');
"""

DADOS = """
INSERT INTO perfil VALUES ('ana'), ('beto');
INSERT INTO token_captura VALUES ('tok-1', 'ana');
INSERT INTO vaga VALUES ('v1', 'ana', 'Vaga Python', 'https://x.com/1', '2026-03-10T09:30:00', 1);
INSERT INTO vaga VALUES ('v2', 'ana', 'Vaga Java', NULL, '2026-03-11T10:00:00', 0);
INSERT INTO candidatura VALUES
  ('c1', 'ana', 'v1', 'cs1', 'Acme', 'Dev', 'APLICADO', '2026-03-10T10:00:00', '2026-03-10T10:00:00', 1),
  ('c2', 'ana', NULL, NULL, 'Beta', 'Dev', 'APLICADO', '2026-03-12T10:00:00', '2026-03-12T10:00:00', 0),
  ('c3', 'beto', NULL, NULL, 'Gama', 'QA', 'OFERTA', '2026-03-13T10:00:00', '2026-03-14T11:00:00', 0);
INSERT INTO perfil_estruturado VALUES
  ('ana', 'Ana Souza', 'ana@x.com', '', 'Resumo', '[{"empresa": "Acme", "cargo": "Dev"}]', '[]', '[]',
   '[{"idioma": "Inglês", "nivel": "AVANCADO"}]', '["Python", "SQL"]');
"""


def criar_sqlite(caminho, extra: str = "", dados: str = DADOS, schema: str = SCHEMA_ANTIGO) -> None:
    conexao = sqlite3.connect(caminho)
    conexao.executescript(schema)
    conexao.executescript(dados)
    conexao.execute(
        "INSERT INTO curriculo_salvo VALUES ('cs1', 'ana', 'Curriculo A', ?, '2026-03-09T08:00:00')", (PDF_A,)
    )
    conexao.execute(
        "INSERT INTO curriculo_salvo VALUES ('cs2', 'beto', 'Curriculo B', ?, '2026-03-09T09:00:00')", (PDF_B,)
    )
    if extra:
        conexao.executescript(extra)
    conexao.commit()
    conexao.close()
