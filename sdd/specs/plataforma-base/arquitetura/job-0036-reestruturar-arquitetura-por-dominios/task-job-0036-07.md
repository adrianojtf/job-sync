# Tarefa 7.0: Migrar domínio vaga_externa

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Migrar os buscadores de vagas externas, extratores de texto, descoberta e candidatura externa para `jobsync/vaga_externa/`, centralizando os clients externos em `adapters`.

<requirements>
- Criar `jobsync/vaga_externa/{domain,service_layer,adapters}`.
- Mover buscadores (Adzuna, Arbeitnow, RemoteOk, WeWorkRemotely, Google CSE) para `adapters/`.
- Mover extratores de texto de páginas para `adapters/`.
- Mover lógica de descoberta/candidatura externa para `service_layer/`.
- Garantir ports em `domain` para fontes externas e extração.
- Ajustar testes.
</requirements>

## Subtarefas

- [ ] 7.1 Criar `vaga_externa/domain` com ports para buscadores e extratores.
- [ ] 7.2 Migrar buscadores de `src/infrastructure/fontes_vagas/` para `adapters/`.
- [ ] 7.3 Migrar extratores de `src/infrastructure/extractors/` para `adapters/`.
- [ ] 7.4 Criar services em `service_layer/` para descoberta e candidatura externa.
- [ ] 7.5 Mover testes para `src/jobsync/tests/vaga_externa/`.

## Detalhes de Implementação

Ver `techspec.md` → Componente `vaga_externa` e Pontos de Integração. Clients externos são `adapters` concretos implementando ports do domínio.

## Critérios de Sucesso

- `pytest` passa para `vaga_externa`.
- Buscadores e extratores estão em `adapters` com sufixo `Client` quando apropriado.
- `domain` não importa HTTP/requests diretamente.

## Testes da Tarefa

- [ ] `pytest src/jobsync/tests/vaga_externa/`
- [ ] Testes com mocks de fontes externas.
- [ ] `import-linter` valida fronteiras.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes
- `src/infrastructure/fontes_vagas/`
- `src/infrastructure/extractors/`
- `src/application/use_cases/` (descoberta/candidatura externa)
- `src/jobsync/vaga_externa/`
