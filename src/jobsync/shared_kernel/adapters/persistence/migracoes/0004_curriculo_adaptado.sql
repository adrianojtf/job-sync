-- Currículo adaptado a uma vaga (JOB-0041): conteúdo estruturado para reedição e reuso como base.
-- curriculo_salvo_id guarda o id do PDF gerado, sem chave estrangeira: remover um currículo
-- salvo é permitido e o currículo adaptado continua existindo (mesma decisão da migração 0002).
CREATE TABLE curriculo_adaptado (
    id TEXT PRIMARY KEY,
    perfil_identificador TEXT NOT NULL REFERENCES perfil(identificador),
    nome_referencia TEXT NOT NULL,
    cargo_alvo TEXT NOT NULL,
    empresa_alvo TEXT NOT NULL,
    idioma_alvo TEXT NOT NULL,
    descricao_vaga TEXT NOT NULL,
    analise_vaga_json JSONB NOT NULL DEFAULT '{}',
    conteudo_json JSONB NOT NULL,
    curriculo_salvo_id TEXT,
    criado_em TIMESTAMPTZ NOT NULL,
    atualizado_em TIMESTAMPTZ NOT NULL
);

CREATE INDEX ix_curriculo_adaptado_perfil ON curriculo_adaptado (perfil_identificador, atualizado_em DESC);
