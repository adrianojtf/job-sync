# Resumo de Tarefas de Implementação de JOB-0047

## Documentos de Referência

- [PRD de JOB-0047](prd-job-0047.md)
- [Tech Spec de JOB-0047](techspec-job-0047.md)

## Tarefas

- [x] 1.0 Domínio: `LinkVaga`, `DadosVaga`, exceções e portas (complexidade: medium; dependências: nenhuma)
- [x] 2.0 Cliente HTTP seguro com proteção contra SSRF (complexidade: high; dependências: nenhuma)
- [x] 3.0 Extrator por IA e leitor genérico de páginas de vaga (complexidade: medium; dependências: 1.0, 2.0)
- [x] 4.0 Leitor do LinkedIn pela versão pública da vaga (complexidade: medium; dependências: 1.0, 2.0)
- [x] 5.0 Limitador em memória e caso de uso `ExtrairDadosVaga` (complexidade: medium; dependências: 1.0, 3.0, 4.0)
- [x] 6.0 Endpoint `POST /v1/vagas/extracoes`, handlers de erro, injeção e configuração (complexidade: medium; dependências: 5.0)
- [x] 7.0 Persistência de cargo, empresa e local na captura de vagas (complexidade: medium; dependências: 1.0)
- [x] 8.0 Frontend: campo "Link da vaga" em Ajustar Vaga e na captura (complexidade: high; dependências: 6.0, 7.0)
- [x] 9.0 Testes E2E com dublê do leitor de vagas (complexidade: medium; dependências: 8.0)
- [x] 10.0 Documentação e validação final (complexidade: low; dependências: 9.0)

## Validação

- [x] O arquivo `resumo-tasks-job-0047.md` está presente e atualizado.
- [x] Todas as tarefas individuais referenciam `prd-job-0047.md` e `techspec-job-0047.md`.
- [x] `lint-imports`, a suíte `pytest` e as suítes do frontend passam.

Resultados da validação final (PostgreSQL local de teste):

| Verificação | Resultado |
|---|---|
| `lint-imports` | 3 contratos mantidos, 0 quebrados |
| `pytest` | 2.173 passaram |
| `npm run lint` | sem erros nem avisos |
| `npm test` (Vitest) | 716 passaram |
| `npm run build` | concluído, com checagem de tipos |
| `npm run e2e` (Playwright) | 69 passaram, incluindo 6 novos e as auditorias de acessibilidade |

### Rastreabilidade dos critérios de aceitação do PRD

| # | Critério | Onde é coberto |
|---|---|---|
| 1 | Link do LinkedIn preenche cargo, empresa, local e descrição, editáveis | `AjustarVagaPageLinkVaga.test.tsx`, E2E `leitura-de-vaga.spec.ts` |
| 2 | Rastreamento removido da URL usada e salva | `test_link_vaga.py`, `ColarVagaModalLink.test.tsx`, E2E |
| 3 | Link de busca com `currentJobId` ou aviso | `test_link_vaga.py`, `test_extracao_vaga_router.py` |
| 4 | Link bloqueado mostra o motivo e permite colar o texto | `test_leitor_vaga_linkedin_client.py`, `test_extracao_vaga_router.py`, E2E |
| 5 | Texto colado preenche os campos com a mesma revisão | `PreencherPeloTexto.test.tsx`, E2E |
| 6 | Link e texto juntos: o texto prevalece | `test_extrair_dados_vaga_service.py` |
| 7 | Endereço interno recusado sem requisição | `test_cliente_http_seguro.py`, `test_extracao_vaga_composicao.py` |
| 8 | Descrição em português, original e sem resumo | `test_leitor_vaga_linkedin_client.py` (também validado contra o HTML real) |
| 9 | Captura só salva após confirmação, com URL normalizada | `ColarVagaModalLink.test.tsx`, E2E |
| 10 | LinkedIn desligado por configuração oferece o texto | `test_extrair_dados_vaga_service.py`, `test_extracao_vaga_composicao.py` |
| 11 | Tempo acima de 15 s vira erro com alternativa | `test_cliente_http_seguro.py`, `test_leitor_vaga_generico_client.py` |

Pendências que dependem de medição ou decisão de produto estão nas "Questões em Aberto" do PRD
(taxa de sucesso do LinkedIn a partir de IPs de servidor, provedor pago de scraping, exibição dos
campos secundários e tratamento de vaga encerrada).
