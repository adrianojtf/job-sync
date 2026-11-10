-- Remover um currículo salvo sempre foi permitido mesmo quando uma candidatura o usa
-- (o SQLite não validava a chave estrangeira) e a tela já lida com currículo ausente.
-- Mantemos esse comportamento: o campo guarda o id, sem obrigar que o currículo exista.
ALTER TABLE candidatura DROP CONSTRAINT IF EXISTS candidatura_curriculo_salvo_id_fkey;
