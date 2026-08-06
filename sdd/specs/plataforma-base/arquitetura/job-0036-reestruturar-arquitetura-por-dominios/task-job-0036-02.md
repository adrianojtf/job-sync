# Tarefa 2.0: Criar shared_kernel/domain

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Identificar e centralizar os value objects e conceitos transversais usados por mais de um domínio, começando por `NomeArquivo` e `CatalogoLocalizacao`, e reavaliar `AnaliseVaga`/`ResultadoAtsScore` conforme dependências cruzadas.

<requirements>
- Criar `src/jobsync/shared_kernel/domain/`.
- Mover `NomeArquivo` para `shared_kernel/domain/nome_arquivo.py`.
- Mover `CatalogoLocalizacao` para `shared_kernel/domain/catalogo_localizacao.py`.
- Reavaliar se `AnaliseVaga` e `ResultadoAtsScore` devem migrar para `shared_kernel` ou permanecer em seus domínios.
- Ajustar imports nos consumidores sem quebrar contratos.
</requirements>

## Subtarefas

- [ ] 2.1 Mapear dependências cruzadas de value objects.
- [ ] 2.2 Criar `shared_kernel/domain/` e mover `NomeArquivo`.
- [ ] 2.3 Mover `CatalogoLocalizacao` (origem: `src/infrastructure/localizacao`).
- [ ] 2.4 Decidir sobre `AnaliseVaga`/`ResultadoAtsScore` e mover se confirmado.
- [ ] 2.5 Atualizar imports nos domínios consumidores.

## Detalhes de Implementação

Ver `techspec.md` → Sequenciamento de Desenvolvimento → Shared kernel e Considerações Técnicas → `shared_kernel`. Value Objects compartilhados eliminam imports diretos entre domínios.

## Critérios de Sucesso

- `NomeArquivo` e `CatalogoLocalizacao` são importáveis de `jobsync.shared_kernel.domain`.
- Domínios acessam esses objetos apenas via `shared_kernel`.
- Decisão documentada para `AnaliseVaga`/`ResultadoAtsScore`.

## Testes da Tarefa

- [ ] Testes de unidade dos value objects em `shared_kernel`.
- [ ] `import-linter` não detecta import de domínio A para domínio B.
- [ ] `pytest` continua passando.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes
- `src/domain/nome_arquivo/`
- `src/infrastructure/localizacao/`
- `src/jobsync/shared_kernel/domain/`
