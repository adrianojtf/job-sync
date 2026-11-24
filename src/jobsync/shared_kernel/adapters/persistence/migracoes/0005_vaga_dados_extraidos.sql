-- Dados lidos da vaga a partir do link ou do texto (JOB-0047): cargo, empresa e local.
-- As colunas são opcionais: vagas capturadas antes desta migração continuam com valores nulos.
ALTER TABLE vaga
    ADD COLUMN cargo TEXT,
    ADD COLUMN empresa TEXT,
    ADD COLUMN local TEXT;
