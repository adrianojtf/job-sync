CREATE TABLE usuario (
    id UUID PRIMARY KEY,
    email TEXT NOT NULL,
    email_verificado BOOLEAN NOT NULL DEFAULT FALSE,
    nome TEXT,
    perfil_identificador TEXT NOT NULL UNIQUE REFERENCES perfil(identificador),
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX ux_usuario_email ON usuario (lower(email));

CREATE TABLE identidade_externa (
    provedor TEXT NOT NULL,
    subject TEXT NOT NULL,
    usuario_id UUID NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
    PRIMARY KEY (provedor, subject)
);

CREATE INDEX ix_identidade_externa_usuario ON identidade_externa (usuario_id);

CREATE TABLE credencial_senha (
    usuario_id UUID PRIMARY KEY REFERENCES usuario(id) ON DELETE CASCADE,
    senha_hash TEXT NOT NULL,
    atualizada_em TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE sessao (
    token_hash BYTEA PRIMARY KEY,
    usuario_id UUID NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
    criada_em TIMESTAMPTZ NOT NULL,
    ultimo_acesso_em TIMESTAMPTZ NOT NULL,
    expira_em TIMESTAMPTZ NOT NULL
);

CREATE INDEX ix_sessao_usuario ON sessao (usuario_id);

CREATE TABLE token_uso_unico (
    token_hash BYTEA PRIMARY KEY,
    usuario_id UUID NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
    finalidade TEXT NOT NULL CHECK (finalidade IN ('confirmacao_email', 'redefinicao_senha')),
    expira_em TIMESTAMPTZ NOT NULL,
    usado_em TIMESTAMPTZ
);

CREATE INDEX ix_token_uso_unico_usuario ON token_uso_unico (usuario_id);

CREATE TABLE estado_oauth (
    estado_hash BYTEA PRIMARY KEY,
    provedor TEXT NOT NULL,
    code_verifier TEXT NOT NULL,
    nonce TEXT NOT NULL,
    destino TEXT NOT NULL,
    expira_em TIMESTAMPTZ NOT NULL
);

CREATE TABLE limite_tentativa (
    chave TEXT PRIMARY KEY,
    contagem INT NOT NULL,
    janela_inicia_em TIMESTAMPTZ NOT NULL,
    bloqueado_ate TIMESTAMPTZ
);
