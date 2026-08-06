# Tarefa 6.0: Migrar domínio core curriculo

<critical>Ler os arquivos de prd.md e techspec.md desta pasta, se você não ler esses arquivos sua tarefa será invalidada</critical>

## Visão Geral

Migrar o domínio `curriculo` (o mais complexo): entidades, ajuste de texto, geração de PDF, carta de apresentação e sugestões ATS. O foco é reorganizar os casos de uso em `service_layer/<funcionalidade>/` e encapsular Groq/PDF em `adapters` com sufixo `Client`.

<requirements>
- Criar `jobsync/curriculo/{domain,service_layer,adapters}`.
- Mover `Curriculo`, `SecaoCurriculo`, `TipoSecao` para `domain`.
- Criar ports em `domain` (`AjustadorTextoPort`, `GeradorPdfPort`, `ExtratorCurriculoPort` etc.).
- Mover `AdaptarCurriculoParaVaga` para `curriculo/service_layer/adaptar_curriculo_para_vaga/service.py`.
- Implementar clients em `adapters` (`AjustadorTextoClient`, `GeradorPdfClient`...).
- Garantir que `domain` não importa Groq, SQLite, PDF ou HTTP.
- Mover e ajustar testes.
</requirements>

## Subtarefas

- [ ] 6.1 Migrar entidades e value objects de `curriculo` para `domain`.
- [ ] 6.2 Criar ports em `curriculo/domain`.
- [ ] 6.3 Migrar `AdaptarCurriculoParaVaga` para `service_layer/adaptar_curriculo_para_vaga/`.
- [ ] 6.4 Migrar serviços de PDF, carta e ATS para `service_layer/<funcionalidade>/`.
- [ ] 6.5 Criar clients `Impl` em `adapters` (`Groq`, `pdf`, `extraction`).
- [ ] 6.6 Ajustar testes para `src/jobsync/tests/curriculo/`.

## Detalhes de Implementação

Ver `techspec.md` → Componente `curriculo` e Design de Implementação. `AdaptarCurriculoParaVaga` depende de ports (`_extrator`, `_analisador_vaga`, `_ajustador_texto`, `_gerador_pdf`) e segue o método `executar`.

## Critérios de Sucesso

- `pytest` passa para `curriculo`.
- `domain` não possui imports de infraestrutura.
- `AdaptarCurriculoParaVaga` funciona com fakes de ports sem alterar comportamento.

## Testes da Tarefa

- [ ] `pytest src/jobsync/tests/curriculo/`
- [ ] Testes de `AdaptarCurriculoParaVaga` com fakes.
- [ ] `import-linter` valida fronteiras de `curriculo`.

<critical>SEMPRE EXECUTE OS TESTES DA TAREFA ANTES DE CONSIDERÁ-LA FINALIZADA</critical>

## Arquivos relevantes
- `src/domain/curriculo/`
- `src/application/use_cases/` (casos de uso relacionados a currículo)
- `src/infrastructure/llm/`
- `src/infrastructure/pdf/`
