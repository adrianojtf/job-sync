CREATE TABLE perfil (
    identificador TEXT PRIMARY KEY
);

CREATE TABLE curriculo_salvo (
    id TEXT PRIMARY KEY,
    perfil_identificador TEXT NOT NULL REFERENCES perfil(identificador),
    nome_referencia TEXT NOT NULL,
    pdf_bytes BYTEA NOT NULL,
    data_upload TIMESTAMPTZ NOT NULL
);

CREATE TABLE token_captura (
    token TEXT PRIMARY KEY,
    perfil_identificador TEXT NOT NULL REFERENCES perfil(identificador)
);

CREATE TABLE vaga (
    id TEXT PRIMARY KEY,
    perfil_identificador TEXT NOT NULL REFERENCES perfil(identificador),
    texto_descricao TEXT NOT NULL,
    url_origem TEXT,
    data_captura TIMESTAMPTZ NOT NULL,
    convertida_em_candidatura BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE candidatura (
    id TEXT PRIMARY KEY,
    perfil_identificador TEXT NOT NULL REFERENCES perfil(identificador),
    vaga_id TEXT REFERENCES vaga(id),
    curriculo_salvo_id TEXT REFERENCES curriculo_salvo(id),
    empresa TEXT NOT NULL,
    cargo TEXT NOT NULL,
    status TEXT NOT NULL,
    data_aplicacao TIMESTAMPTZ NOT NULL,
    data_ultima_mudanca_status TIMESTAMPTZ NOT NULL,
    posicao INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE perfil_estruturado (
    perfil_identificador TEXT PRIMARY KEY REFERENCES perfil(identificador),
    nome_completo TEXT NOT NULL,
    email TEXT NOT NULL,
    linkedin TEXT NOT NULL DEFAULT '',
    resumo_profissional TEXT NOT NULL DEFAULT '',
    experiencias_json JSONB NOT NULL DEFAULT '[]',
    formacoes_json JSONB NOT NULL DEFAULT '[]',
    certificacoes_json JSONB NOT NULL DEFAULT '[]',
    idiomas_json JSONB NOT NULL DEFAULT '[]',
    tecnologias_json JSONB NOT NULL DEFAULT '[]'
);
