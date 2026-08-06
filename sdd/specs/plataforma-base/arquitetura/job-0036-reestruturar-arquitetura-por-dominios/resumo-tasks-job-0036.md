# Resumo de Tarefas — Reestruturar o projeto para a arquitetura por domínios

## Visão Geral

Refatoração pura de arquitetura: migrar o código de `src/{application,domain,infrastructure,ui}` para `src/jobsync/<dominio>/{domain,service_layer,adapters}`, centralizar `entrypoints`, extrair `shared_kernel` e garantir conformidade via `import-linter`. Nenhum contrato, endpoint ou comportamento é alterado.

## Tarefas

- [ ] 1.0 Preparar ambiente de migração: criar `src/jobsync/`, ajustar `pytest.ini`, `PYTHONPATH`, adicionar `import-linter` e atualizar `requirements.txt`
- [x] 2.0 Criar `shared_kernel/domain` com `NomeArquivo` e `CatalogoLocalizacao`; reavaliar `AnaliseVaga`/`ResultadoAtsScore`
- [x] 3.0 Migrar domínios folha: `ats_score` e `token_captura`
- [x] 4.0 Migrar domínios com persistência simples: `perfil`, `curriculo_salvo` e `vaga`
- [ ] 5.0 Migrar domínios de negócio: `candidatura` e `perfil_estruturado`
- [ ] 6.0 Migrar domínio core: `curriculo` (adaptação, PDF, carta, ATS)
- [ ] 7.0 Migrar domínio `vaga_externa` (buscadores, extração, descoberta, candidatura externa)
- [ ] 8.0 Migrar `entrypoints`: `streamlit_app.py` e `servidor_captura.py`
- [ ] 9.0 Configurar contratos `import-linter` e testes de arquitetura
- [ ] 10.0 Limpar diretórios legacy e atualizar `README.md`

## Detalhamento

| # | Título | Complexidade | Dependências | Testes Principais |
|---|--------|--------------|--------------|-------------------|
| 1.0 | Preparar ambiente de migração | medium | — | `pytest` passa; `import-linter` instalado e configurável |
| 2.0 | Criar `shared_kernel/domain` | medium | 1.0 | Testes de importação e reavaliação dos shared value objects |
| 3.0 | Migrar `ats_score` e `token_captura` | low | 1.0, 2.0 | `pytest` do domínio passa; sem imports cíclicos |
| 4.0 | Migrar `perfil`, `curriculo_salvo` e `vaga` | medium | 1.0, 2.0 | Testes dos repositórios `Impl` e services ajustados |
| 5.0 | Migrar `candidatura` e `perfil_estruturado` | medium | 1.0, 2.0, 4.0 | `pytest` por domínio; DTOs e `executar` validados |
| 6.0 | Migrar `curriculo` | high | 1.0, 2.0, 4.0, 5.0 | Testes de `AdaptarCurriculoParaVaga` e ports; PDF/ATS intactos |
| 7.0 | Migrar `vaga_externa` | medium | 1.0, 2.0, 4.0 | Testes de buscadores e extração; imports ajustados |
| 8.0 | Migrar `entrypoints` | medium | 3.0, 4.0, 5.0, 6.0, 7.0 | App Streamlit sobe; endpoint `/api/vagas/capturar` responde |
| 9.0 | Configurar `import-linter` e testes de arquitetura | medium | 1.0 a 8.0 | `lint-imports` passa; ciclos e dependências proibidas bloqueadas |
| 10.0 | Limpar diretórios legacy e atualizar `README.md` | low | 9.0 | `pytest` e `lint-imports` continuam passando; documentação atualizada |

## Arquivos de origem

- PRD: `prd-job-0036.md`
- Tech Spec: `techspec-job-0036.md`
