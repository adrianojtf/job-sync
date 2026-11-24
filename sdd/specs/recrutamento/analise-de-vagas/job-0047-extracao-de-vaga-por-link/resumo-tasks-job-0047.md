# Resumo de Tarefas de Implementação de JOB-0047

## Documentos de Referência

- [PRD de JOB-0047](prd-job-0047.md)
- [Tech Spec de JOB-0047](techspec-job-0047.md)

## Tarefas

- [x] 1.0 Domínio: `LinkVaga`, `DadosVaga`, exceções e portas (complexidade: medium; dependências: nenhuma)
- [x] 2.0 Cliente HTTP seguro com proteção contra SSRF (complexidade: high; dependências: nenhuma)
- [x] 3.0 Extrator por IA e leitor genérico de páginas de vaga (complexidade: medium; dependências: 1.0, 2.0)
- [x] 4.0 Leitor do LinkedIn pela versão pública da vaga (complexidade: medium; dependências: 1.0, 2.0)
- [ ] 5.0 Limitador em memória e caso de uso `ExtrairDadosVaga` (complexidade: medium; dependências: 1.0, 3.0, 4.0)
- [ ] 6.0 Endpoint `POST /v1/vagas/extracoes`, handlers de erro, injeção e configuração (complexidade: medium; dependências: 5.0)
- [ ] 7.0 Persistência de cargo, empresa e local na captura de vagas (complexidade: medium; dependências: 1.0)
- [ ] 8.0 Frontend: campo "Link da vaga" em Ajustar Vaga e na captura (complexidade: high; dependências: 6.0, 7.0)
- [ ] 9.0 Testes E2E com dublê do leitor de vagas (complexidade: medium; dependências: 8.0)
- [ ] 10.0 Documentação e validação final (complexidade: low; dependências: 9.0)

## Validação

- [ ] O arquivo `resumo-tasks-job-0047.md` está presente e atualizado.
- [ ] Todas as tarefas individuais referenciam `prd-job-0047.md` e `techspec-job-0047.md`.
- [ ] `lint-imports`, a suíte `pytest` e as suítes do frontend passam.
